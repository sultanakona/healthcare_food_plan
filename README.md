# 🍎 AI Nutrition Recommendation System

**Personalized meal planning powered by Linear Programming optimization and FastAPI**

---

## 📋 Overview

This system generates personalized daily and weekly meal plans based on:
- User demographics (age, gender, height, weight)
- Activity level and fitness goals
- Health conditions (diabetes, hypertension, etc.)
- Food allergies and dietary restrictions
- Evidence-based nutritional guidelines (WHO, EFSA)

### Key Features

✅ **Rule-Based Safety**: Filters meals by allergies, conditions, and dietary restrictions  
✅ **LP Optimization**: Uses PuLP to solve nutritional targets optimally  
✅ **Fast API**: RESTful API with automatic documentation  
✅ **Realistic Meals**: Smart filtering prevents unrealistic food combinations  
✅ **Weekly Planning**: Generate 1-14 days of meal plans  

---

## 🏗️ Project Structure

```
ai_nutrition/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI application
│   ├── optimizer/
│   │   ├── engine.py            # Main optimization engine
│   │   └── lp_day_solver.py     # LP-based meal solver
│   ├── profile/
│   │   └── profile_builder.py   # User profile & targets
│   ├── pipelines/               # Data processing pipelines
│   └── config.py                # Configuration
├── data_raw/                    # Raw data files (FDC, INFOODS, etc.)
├── data_intermediate/           # Processed intermediate files
├── data_output/                 # Final outputs
│   ├── foods_complete_with_portions.csv
│   ├── user_targets.json
│   └── meal_plan_lp.json
├── tests/                       # Unit tests
├── docs/                        # Documentation
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- pip

### 2. Installation

```bash
# Clone or extract the project
cd ai_nutrition

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Prepare Food Database

Place your food database CSV at:
```
data_output/foods_complete_with_portions.csv
```

**Required columns:**
- `food_id` or auto-generated
- `food_name` (or `description`)
- `calories` (or `energy_kcal`)
- `protein` (or `protein_g`)
- `fat` (or `total_fat`, `fat_g`)
- `carbs` (or `carbohydrate`, `carb`)
- `fiber` (optional, or `dietary_fiber`)
- `grams_per_portion` (defaults to 100g)
- `portion_unit` (defaults to "portion")

### 4. Run the API

```bash
# Using main.py
python main.py api

# Or directly with uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### Health Check

**GET** `/`
```json
{
  "status": "running",
  "service": "AI Nutrition Recommendation System",
  "foods_loaded": 5000
}
```

### Calculate Targets

**POST** `/api/v1/calculate_targets`

**Request Body:**
```json
{
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
```

**Response:**
```json
{
  "status": "success",
  "profile": {
    "inputs": {...},
    "metrics": {
      "bmi": 24.49,
      "bmr_kcal": 1728.8,
      "tdee_kcal": 2679.6
    },
    "targets": {
      "calories": 2679.6,
      "protein_g": 105.0,
      "fat_g": 83.5,
      "carbs_g": 326.2,
      "fiber_g": 30.0
    }
  }
}
```

### Generate Daily Plan

**POST** `/api/v1/generate_daily_plan`

**Request Body:** Same as `/calculate_targets`

**Response:**
```json
{
  "status": "success",
  "date": "2026-02-03",
  "profile": {...},
  "plan": {
    "meals": {
      "breakfast": [...],
      "snack1": [...],
      "lunch": [...],
      "snack2": [...],
      "dinner": [...]
    },
    "totals": {
      "calories": 2650.3,
      "protein": 103.8,
      "fat": 81.2,
      "carbs": 320.5,
      "fiber": 28.7
    },
    "warnings": []
  }
}
```

### Generate Weekly Plan

**POST** `/api/v1/generate_weekly_plan`

**Request Body:**
```json
{
  "profile": {
    "age": 30,
    "gender": "male",
    ...
  },
  "days": 7
}
```

### Get Foods

**GET** `/api/v1/foods?limit=100&search=chicken`

### Download Meal Plan

**GET** `/api/v1/download/meal_plan`

---

## 🎯 Usage Examples

### Python Client

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# User profile
profile = {
    "age": 25,
    "gender": "female",
    "height_cm": 165,
    "weight_kg": 60,
    "activity": "moderate",
    "goal": "weight_loss",
    "intensity": "standard",
    "conditions": [],
    "allergies": ["peanut", "dairy"]
}

# Generate daily plan
response = requests.post(
    f"{BASE_URL}/api/v1/generate_daily_plan",
    json=profile
)

plan = response.json()
print(plan["plan"]["totals"])
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/calculate_targets" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 30,
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 75,
    "activity": "moderate",
    "goal": "maintain"
  }'
```

---

## 🔧 Configuration

### Activity Levels
- `sedentary`: 1.2x BMR
- `lightly`: 1.375x BMR
- `moderate`: 1.55x BMR (default)
- `very`: 1.725x BMR
- `athlete`: 1.9x BMR

### Goals
- `maintain`: TDEE (no deficit/surplus)
- `weight_loss`: 15-25% deficit
- `muscle_gain`: 5-15% surplus
- `diabetes_control`: 5% deficit + high protein

### Intensity
- `mild`: 5-15% adjustment
- `standard`: 10-20% adjustment (default)
- `aggressive`: 15-25% adjustment

### Allergies
Supported: `peanut`, `nuts`, `tree_nut`, `dairy`, `egg`, `seafood`, `fish`

### Conditions
Supported: `diabetes`, `hypertension`, `cardiovascular`

---

## 📊 Data Processing Pipeline

Run data pipelines (if you have raw data):

```bash
python main.py pipeline --steps step1 step2 step3
```

**Pipeline Steps:**
1. **step1**: Build master FDC table
2. **step2**: Process portions and densities
3. **step3**: Build complete food database
4. **step4**: Integration tests

---

## 🧪 Testing

```bash
# Run all tests
python main.py test

# Or use pytest
pytest tests/
```

---

## 🛠️ Development

### Adding New Features

1. **New API Endpoint**: Add to `src/api/main.py`
2. **New Optimizer Logic**: Modify `src/optimizer/engine.py` or `lp_day_solver.py`
3. **New Profile Rules**: Edit `src/profile/profile_builder.py`

### Code Style

```bash
# Format code
black src/

# Check types
mypy src/

# Lint
flake8 src/
```

---

## 📝 Environment Variables

Create a `.env` file (optional):

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Database paths
FOODS_DATABASE_PATH=data_output/foods_complete_with_portions.csv

# Optimization parameters
LP_SOLVER_TIMEOUT=10
MAX_CANDIDATES_PER_MEAL=250
```

---

## 🐛 Troubleshooting

### Issue: "Food database not available"

**Solution**: Ensure `data_output/foods_complete_with_portions.csv` exists

```bash
# Check if file exists
ls -lh data_output/foods_complete_with_portions.csv

# If missing, run data pipeline or add sample data
```

### Issue: LP solver fails

**Solution**: Check PuLP installation

```bash
pip install --upgrade PuLP
```

### Issue: Import errors

**Solution**: Run from project root

```bash
# Correct
cd ai_nutrition
python main.py api

# Incorrect
cd ai_nutrition/src
python api/main.py  # ❌
```

---

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (interactive)
- **ReDoc**: http://localhost:8000/redoc (alternative UI)
- **Technical Spec**: See `docs/AI_Nutrition_Recommendation_System.docx`

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is for educational purposes.

---

## 🙏 Acknowledgments

- **USDA FoodData Central** for nutrient data
- **FAO/INFOODS** for regional food composition tables
- **PuLP** for linear programming solver
- **FastAPI** for modern API framework

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Python, FastAPI, and Linear Programming**
