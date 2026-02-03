"""
Complete Optimizer Engine
Integrates profile building and day planning for the API
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

# Import from profile_builder
from src.profile.profile_builder import build_profile_targets

# Import from lp_day_solver
from src.optimizer.lp_day_solver import build_day as lp_build_day


def build_profile(
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    activity: str = "moderate",
    goal: str = "maintain",
    intensity: str = "standard",
    conditions: Optional[List[str]] = None,
    allergies: Optional[List[str]] = None,
) -> Dict:
    """
    Wrapper around profile_builder for API compatibility
    """
    return build_profile_targets(
        age=age,
        gender=gender,
        height_cm=height_cm,
        weight_kg=weight_kg,
        activity=activity,
        goal=goal,
        intensity=intensity,
        conditions=conditions,
        allergies=allergies,
    )


def build_day(profile: Dict, foods_df: pd.DataFrame) -> Dict:
    """
    Build a complete daily meal plan using LP optimization
    
    Args:
        profile: User profile dict with 'targets', 'inputs' keys
        foods_df: DataFrame with food database
    
    Returns:
        Dict with 'meals', 'totals', 'warnings'
    """
    targets = profile.get("targets", {})
    inputs = profile.get("inputs", {})
    
    allergies = inputs.get("allergies", [])
    conditions = inputs.get("conditions", [])
    
    # Call the LP solver
    plan = lp_build_day(
        foods_df=foods_df,
        targets=targets,
        allergies=allergies,
        conditions=conditions,
    )
    
    return plan


def build_weekly_plan(profile: Dict, foods_df: pd.DataFrame, days: int = 7) -> Dict:
    """
    Build a weekly meal plan (multiple days)
    
    Args:
        profile: User profile
        foods_df: Food database
        days: Number of days to generate (default 7)
    
    Returns:
        Dict with weekly plan structure
    """
    weekly = {"days": [], "weekly_totals": {}, "warnings": []}
    
    grand_totals = {
        "calories": 0.0,
        "protein": 0.0,
        "fat": 0.0,
        "carbs": 0.0,
        "fiber": 0.0
    }
    
    for day_num in range(1, days + 1):
        day_plan = build_day(profile, foods_df)
        day_plan["day_number"] = day_num
        
        # Accumulate totals
        for nutrient in grand_totals:
            grand_totals[nutrient] += day_plan["totals"].get(nutrient, 0.0)
        
        weekly["days"].append(day_plan)
        
        # Collect warnings
        if day_plan.get("warnings"):
            weekly["warnings"].extend([f"Day {day_num}: {w}" for w in day_plan["warnings"]])
    
    # Calculate averages
    weekly["weekly_totals"] = {
        f"{k}_total": round(v, 2) for k, v in grand_totals.items()
    }
    weekly["daily_averages"] = {
        f"{k}_avg": round(v / days, 2) for k, v in grand_totals.items()
    }
    
    return weekly
