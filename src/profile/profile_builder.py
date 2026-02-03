import json
from dataclasses import dataclass
from typing import List, Optional, Dict
from src import config

ACTIVITY_FACTOR = {
    "sedentary": 1.2,
    "lightly":   1.375,
    "moderate":  1.55,
    "very":      1.725,
    "athlete":   1.9,
}

def build_profile_targets(
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
    conditions = conditions or []
    allergies = allergies or []

    bmi = weight_kg / (height_cm / 100) ** 2
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    bmr = base + 5 if gender.lower().startswith("m") else base - 161
    tdee = bmr * ACTIVITY_FACTOR.get(activity.lower(), 1.55)

    goal_l = goal.lower()
    if goal_l in ["weight_loss", "fat_loss", "loss"]:
        deficit = {"mild": 0.15, "standard": 0.20, "aggressive": 0.25}.get(intensity, 0.20)
        target_cal = tdee * (1 - deficit)
    elif goal_l in ["muscle_gain", "gain", "bulking"]:
        surplus = {"mild": 0.05, "standard": 0.10, "aggressive": 0.15}.get(intensity, 0.10)
        target_cal = tdee * (1 + surplus)
    elif goal_l in ["diabetes_control", "disease_control"]:
        target_cal = tdee * 0.95
    else:
        target_cal = tdee

    has_diabetes = any("diabetes" in c.lower() for c in conditions)

    if goal_l in ["muscle_gain", "gain", "bulking"]:
        protein_g = 1.8 * weight_kg
        fat_ratio = 0.25
    elif goal_l in ["weight_loss", "fat_loss", "loss"]:
        protein_g = 1.6 * weight_kg
        fat_ratio = 0.30
    else:
        protein_g = 1.4 * weight_kg
        fat_ratio = 0.28

    if has_diabetes:
        protein_g = max(protein_g, 1.6 * weight_kg)
        fat_ratio = max(fat_ratio, 0.30)

    fat_g = target_cal * fat_ratio / 9
    carbs_g = max(0, (target_cal - protein_g * 4 - fat_g * 9) / 4)
    fiber_g = 30.0 if (target_cal < 2200 or has_diabetes) else 25.0

    profile = {
        "inputs": {
            "age": age,
            "gender": gender,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "activity": activity,
            "goal": goal,
            "intensity": intensity,
            "conditions": conditions,
            "allergies": allergies,
        },
        "metrics": {
            "bmi": round(bmi, 2),
            "bmr_kcal": round(bmr, 1),
            "tdee_kcal": round(tdee, 1),
        },
        "targets": {
            "calories": round(target_cal, 1),
            "protein_g": round(protein_g, 1),
            "fat_g": round(fat_g, 1),
            "carbs_g": round(carbs_g, 1),
            "fiber_g": round(fiber_g, 1),
        },
    }

    # ✅ Save to data_output/user_targets.json
    config.DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.USER_TARGETS_JSON, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

    return profile
