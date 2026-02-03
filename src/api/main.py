"""
Complete FastAPI Application for AI Nutrition Recommendation System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import pandas as pd
from datetime import date, datetime
import json
import logging

from src.config import DATA_OUT, FOODS_COMPLETE_CSV, USER_TARGETS_JSON, MEAL_PLAN_JSON
from src.optimizer.engine import build_profile, build_day, build_weekly_plan

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Nutrition Recommendation System",
    description="Personalized meal planning with LP optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load food database on startup
foods_db = None

@app.on_event("startup")
async def load_food_database():
    global foods_db
    try:
        if FOODS_COMPLETE_CSV.exists():
            foods_db = pd.read_csv(FOODS_COMPLETE_CSV)
            logger.info(f"✅ Loaded {len(foods_db)} foods from database")
        else:
            logger.warning(f"⚠️ Food database not found at {FOODS_COMPLETE_CSV}")
            # Create a minimal sample database for testing
            foods_db = pd.DataFrame({
                'food_id': range(100),
                'food_name': [f'Sample Food {i}' for i in range(100)],
                'calories': [i * 10 for i in range(100)],
                'protein': [i * 0.5 for i in range(100)],
                'fat': [i * 0.3 for i in range(100)],
                'carbs': [i * 0.8 for i in range(100)],
                'fiber': [i * 0.1 for i in range(100)],
                'grams_per_portion': [100] * 100,
                'portion_unit': ['portion'] * 100,
            })
            logger.info("Created sample food database for testing")
    except Exception as e:
        logger.error(f"❌ Error loading food database: {e}")
        foods_db = pd.DataFrame()


# Pydantic models
class UserProfile(BaseModel):
    age: int = Field(..., ge=10, le=100, description="Age in years")
    gender: str = Field(..., description="Gender: 'male' or 'female'")
    height_cm: float = Field(..., ge=100, le=250, description="Height in centimeters")
    weight_kg: float = Field(..., ge=30, le=300, description="Weight in kilograms")
    activity: str = Field(default="moderate", description="Activity level: sedentary, lightly, moderate, very, athlete")
    goal: str = Field(default="maintain", description="Goal: maintain, weight_loss, muscle_gain, diabetes_control")
    intensity: str = Field(default="standard", description="Intensity: mild, standard, aggressive")
    conditions: List[str] = Field(default_factory=list, description="Health conditions: e.g., ['diabetes', 'hypertension']")
    allergies: List[str] = Field(default_factory=list, description="Allergies: e.g., ['peanut', 'dairy', 'seafood']")

    class Config:
        schema_extra = {
            "example": {
                "age": 30,
                "gender": "male",
                "height_cm": 175,
                "weight_kg": 75,
                "activity": "moderate",
                "goal": "maintain",
                "intensity": "standard",
                "conditions": [],
                "allergies": []
            }
        }


class WeeklyPlanRequest(BaseModel):
    profile: UserProfile
    days: int = Field(default=7, ge=1, le=14, description="Number of days to generate")


# API Endpoints

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "AI Nutrition Recommendation System",
        "version": "1.0.0",
        "foods_loaded": len(foods_db) if foods_db is not None else 0,
        "database_ready": foods_db is not None and len(foods_db) > 0
    }


@app.get("/api/v1/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "loaded": foods_db is not None,
            "food_count": len(foods_db) if foods_db is not None else 0,
            "path": str(FOODS_COMPLETE_CSV)
        },
        "directories": {
            "data_output": str(DATA_OUT),
            "exists": DATA_OUT.exists()
        }
    }


@app.post("/api/v1/calculate_targets")
def calculate_targets(user: UserProfile):
    """
    Calculate nutritional targets for a user profile
    Returns BMI, BMR, TDEE, and macro targets
    """
    try:
        profile = build_profile(**user.model_dump())
        logger.info(f"✅ Calculated targets for user: {user.age}y, {user.gender}, {user.goal}")
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "profile": profile
        }
    except Exception as e:
        logger.error(f"❌ Error calculating targets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate_daily_plan")
def generate_daily_plan(user: UserProfile):
    """
    Generate a complete daily meal plan optimized for the user's targets
    """
    if foods_db is None or len(foods_db) == 0:
        raise HTTPException(
            status_code=503,
            detail="Food database not available. Please ensure the database is loaded."
        )
    
    try:
        # Build profile
        profile = build_profile(**user.model_dump())
        
        # Generate meal plan
        plan = build_day(profile, foods_db)
        
        # Save to file
        output_data = {
            "date": str(date.today()),
            "timestamp": datetime.now().isoformat(),
            "profile": profile,
            "plan": plan
        }
        
        with open(MEAL_PLAN_JSON, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Generated daily plan for user")
        
        return {
            "status": "success",
            "date": str(date.today()),
            "profile": profile,
            "plan": plan
        }
    except Exception as e:
        logger.error(f"❌ Error generating daily plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate_weekly_plan")
def generate_weekly_plan(request: WeeklyPlanRequest):
    """
    Generate a weekly meal plan (7 days by default)
    """
    if foods_db is None or len(foods_db) == 0:
        raise HTTPException(
            status_code=503,
            detail="Food database not available."
        )
    
    try:
        # Build profile
        profile = build_profile(**request.profile.model_dump())
        
        # Generate weekly plan
        weekly = build_weekly_plan(profile, foods_db, days=request.days)
        
        logger.info(f"✅ Generated {request.days}-day plan")
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "profile": profile,
            "weekly_plan": weekly
        }
    except Exception as e:
        logger.error(f"❌ Error generating weekly plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/foods")
def get_foods(limit: int = 100, search: Optional[str] = None):
    """
    Get list of available foods in database
    """
    if foods_db is None or len(foods_db) == 0:
        raise HTTPException(status_code=503, detail="Food database not available")
    
    try:
        df = foods_db.copy()
        
        if search:
            df = df[df['food_name'].str.contains(search, case=False, na=False)]
        
        df = df.head(limit)
        
        foods_list = df.to_dict(orient='records')
        
        return {
            "status": "success",
            "count": len(foods_list),
            "total_foods": len(foods_db),
            "search": search,
            "foods": foods_list
        }
    except Exception as e:
        logger.error(f"❌ Error retrieving foods: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/download/meal_plan")
def download_meal_plan():
    """
    Download the last generated meal plan as JSON
    """
    if not MEAL_PLAN_JSON.exists():
        raise HTTPException(status_code=404, detail="No meal plan found. Generate one first.")
    
    return FileResponse(
        path=MEAL_PLAN_JSON,
        media_type="application/json",
        filename=f"meal_plan_{date.today()}.json"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
