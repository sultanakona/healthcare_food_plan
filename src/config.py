from pathlib import Path

# Project root = .../ai_nutrition
ROOT_DIR = Path(__file__).resolve().parents[1]

# Directory structure
DATA_OUTPUT_DIR = ROOT_DIR / "data_output"
DATA_INTERMEDIATE_DIR = ROOT_DIR / "data_intermediate"
DATA_RAW_DIR = ROOT_DIR / "data_raw"

# Alias for backward compatibility
DATA_OUT = DATA_OUTPUT_DIR

# Master food database
FOODS_MASTER_CSV = DATA_OUTPUT_DIR / "master_food_table_fdc_full.csv"
FOODS_COMPLETE_CSV = DATA_OUTPUT_DIR / "foods_complete_with_portions.csv"

# User profile and meal plan outputs
USER_TARGETS_JSON = DATA_OUTPUT_DIR / "user_targets.json"
MEAL_PLAN_JSON = DATA_OUTPUT_DIR / "meal_plan_lp.json"
MEAL_PLAN_CSV = DATA_OUTPUT_DIR / "meal_plan_lp.csv"

# Ensure directories exist
for directory in [DATA_OUTPUT_DIR, DATA_INTERMEDIATE_DIR, DATA_RAW_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
