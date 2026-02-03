import numpy as np
import pandas as pd

from pulp import (
    LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value, PULP_CBC_CMD
)

# ============================================================
# FIXED LP DAY SOLVER (stable + realistic + no scope bugs)
# ============================================================

# ---- hard caps per 100g (prevents garbage rows breaking LP)
MAX_KCAL_100G   = 900.0
MAX_PRO_100G    = 100.0
MAX_FAT_100G    = 100.0
MAX_CARBS_100G  = 120.0
MAX_FIBER_100G  = 80.0

BLACKLIST = [
    "dried", "powder", "flakes", "dehydrated", "concentrate",
    "instant", "seasoning", "bouillon", "broth, dry",
    "whipped", "imitation", "analog", "textured", "extract",
    "condensed", "evaporated",
]

MEAL_RULES = {
    "breakfast": {
        "keywords": ["oat","egg","milk","cereal","banana","yogurt","toast","pancake","rice","bread","orange","apple"],
        "blocked":  ["fish","beef","chicken","pork","shrimp","tuna","salmon","mutton","lamb","devilfish","winged"],
    },
    "snack": {
        "keywords": ["apple","banana","orange","yogurt","almond","biscuit","bread",
                     "fruit","tea","coffee","milk","grape","berry","cookie","cracker","nut"],
        "blocked":  ["fish","beef","chicken","pork","rice","curry","dried","powder","condensed","mutton","devilfish","winged","bean","kidney"],
    },
    "lunch": {
        "keywords": ["rice","chicken","fish","dal","lentil","bean","vegetable","egg",
                     "paneer","tofu","mutton","shrimp","potato","noodle","pasta","chickpea"],
        "blocked":  ["candy","cake","sweet","chocolate","soda","syrup","devilfish","winged"],
    },
    "dinner": {
        "keywords": ["chicken","fish","dal","lentil","bean","egg","vegetable",
                     "paneer","tofu","rice","potato","mushroom","broccoli","spinach","salmon","chickpea"],
        "blocked":  ["candy","cake","sweet","chocolate","soda","syrup","devilfish","winged"],
    },
}

MEAL_CONFIG = {
    "breakfast": (0.25,  2, 3, "breakfast"),
    "snack1":    (0.10,  1, 2, "snack"),
    "lunch":     (0.30,  2, 4, "lunch"),
    "snack2":    (0.10,  1, 2, "snack"),
    "dinner":    (0.25,  2, 4, "dinner"),
}


# ---------------------------
# utils
# ---------------------------

def _to_num(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    s = s.replace([np.inf, -np.inf], np.nan)
    return s

def _ensure_required_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    rename_map = {}
    if "food_name" not in out.columns:
        for alt in ["description", "name", "FoodName"]:
            if alt in out.columns:
                rename_map[alt] = "food_name"
                break

    if "calories" not in out.columns:
        for alt in ["energy_kcal", "kcal", "Energy_kcal", "EnergyKcal"]:
            if alt in out.columns:
                rename_map[alt] = "calories"
                break

    if "protein" not in out.columns:
        for alt in ["protein_g", "Protein_g", "Protein"]:
            if alt in out.columns:
                rename_map[alt] = "protein"
                break

    if "fat" not in out.columns:
        for alt in ["fat_g", "total_fat", "TotalFat_g", "TotalFat"]:
            if alt in out.columns:
                rename_map[alt] = "fat"
                break

    if "carbs" not in out.columns:
        for alt in ["carbohydrate", "carbohydrate_g", "carb", "Carbohydrate_g", "Carbohydrate"]:
            if alt in out.columns:
                rename_map[alt] = "carbs"
                break

    if "fiber" not in out.columns:
        for alt in ["dietary_fiber", "fiber_g", "DietaryFiber_g", "DietaryFiber"]:
            if alt in out.columns:
                rename_map[alt] = "fiber"
                break

    if rename_map:
        out = out.rename(columns=rename_map)

    if "food_id" not in out.columns:
        out["food_id"] = np.arange(len(out))

    if "portion_unit" not in out.columns:
        out["portion_unit"] = "portion"

    if "grams_per_portion" not in out.columns:
        # assume per 100g basis
        out["grams_per_portion"] = 100.0

    if "fiber" not in out.columns:
        out["fiber"] = 0.0

    if "name_norm" not in out.columns:
        out["name_norm"] = out["food_name"].astype(str).str.lower()

    # numeric cast
    for c in ["calories", "protein", "fat", "carbs", "fiber", "grams_per_portion"]:
        out[c] = _to_num(out[c])

    # drop invalid rows
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=["food_name", "calories", "protein", "fat", "carbs", "grams_per_portion"]).copy()

    # non-negative
    for c in ["calories", "protein", "fat", "carbs", "fiber", "grams_per_portion"]:
        out = out[out[c] >= 0]

    # hard caps (stops 12700 carbs etc)
    out.loc[out["calories"] > MAX_KCAL_100G, "calories"] = MAX_KCAL_100G
    out.loc[out["protein"]  > MAX_PRO_100G,  "protein"]  = MAX_PRO_100G
    out.loc[out["fat"]      > MAX_FAT_100G,  "fat"]      = MAX_FAT_100G
    out.loc[out["carbs"]    > MAX_CARBS_100G,"carbs"]    = MAX_CARBS_100G
    out.loc[out["fiber"]    > MAX_FIBER_100G,"fiber"]    = MAX_FIBER_100G

    # basic validity
    out = out[(out["calories"] > 0) & (out["grams_per_portion"] > 0)].reset_index(drop=True)

    # stable ids
    out["food_id"] = out["food_id"].astype(str)

    return out


def filter_by_user(df: pd.DataFrame, allergies: list, conditions: list) -> pd.DataFrame:
    allergies  = [a.lower() for a in (allergies or [])]
    conditions = [c.lower() for c in (conditions or [])]
    out = df.copy()

    allergy_map = {
        "peanut":   r"peanut",
        "nuts":     r"almond|cashew|walnut|pistachio|pecan|nut",
        "tree_nut": r"almond|cashew|walnut|pistachio|pecan|nut",
        "dairy":    r"milk|cheese|yogurt|butter|cream|whey|casein",
        "egg":      r"egg",
        "seafood":  r"fish|shrimp|crab|salmon|tuna|cod|sardine|lobster|tilapia",
        "fish":     r"fish|shrimp|crab|salmon|tuna|cod|sardine|lobster|tilapia",
    }

    for a in allergies:
        pattern = allergy_map.get(a)
        if pattern:
            out = out[~out["name_norm"].str.contains(pattern, na=False)]

    if any("diabetes" in c for c in conditions):
        out = out[~out["name_norm"].str.contains(
            r"sugar|soda|candy|cake|sweet|chocolate|syrup|jam", na=False)]

    return out.reset_index(drop=True)


def get_pool(df: pd.DataFrame, slot: str, max_candidates: int = 250) -> pd.DataFrame:
    rules = MEAL_RULES[slot]
    out = df.copy()

    # blacklist
    for kw in BLACKLIST:
        out = out[~out["name_norm"].str.contains(kw, na=False)]

    # blocked
    for kw in rules["blocked"]:
        out = out[~out["name_norm"].str.contains(kw, na=False)]

    # strict keywords
    pattern = "|".join(rules["keywords"])
    strict = out[out["name_norm"].str.contains(pattern, na=False)].reset_index(drop=True)

    # fallback if strict empty
    if strict.empty:
        strict = out.copy()

    # sample for speed + variety
    if len(strict) > max_candidates:
        strict["_score"] = (
            (strict["protein"] / (strict["calories"] + 1e-6)) * 0.35 +
            (strict["fiber"]   / (strict["calories"] + 1e-6)) * 0.25 +
            np.random.rand(len(strict)) * 0.40
        )
        strict = strict.sort_values("_score", ascending=False).head(max_candidates)
        strict = strict.drop(columns=["_score"]).reset_index(drop=True)

    return strict


# ---------------------------
# LP solver
# ---------------------------

def solve_one_meal(
    pool: pd.DataFrame,
    target_cal: float,
    macro_target: dict,
    max_items: int = 3,
    min_items: int = 1,
):
    if pool.empty:
        return None

    rows = pool.reset_index(drop=True)

    # arrays (per-portion = grams_per_portion/100 scaling)
    cal = []
    pro = []
    fat = []
    carb = []
    fib = []

    for _, r in rows.iterrows():
        gpp = float(r["grams_per_portion"])
        scale = gpp / 100.0

        cal.append(float(r["calories"]) * scale)
        pro.append(float(r["protein"])  * scale)
        fat.append(float(r["fat"])      * scale)
        carb.append(float(r["carbs"])   * scale)
        fib.append(float(r.get("fiber", 0.0)) * scale)

    n = len(rows)
    solver = PULP_CBC_CMD(msg=0, timeLimit=10)

    x = {i: LpVariable(f"x{i}", lowBound=0, upBound=1.5) for i in range(n)}
    y = {i: LpVariable(f"y{i}", cat="Binary") for i in range(n)}

    T_cal  = lpSum(cal[i]  * x[i] for i in range(n))
    T_pro  = lpSum(pro[i]  * x[i] for i in range(n))
    T_fat  = lpSum(fat[i]  * x[i] for i in range(n))
    T_carb = lpSum(carb[i] * x[i] for i in range(n))
    T_fib  = lpSum(fib[i]  * x[i] for i in range(n))

    prob = LpProblem("meal", LpMinimize)

    for i in range(n):
        prob += x[i] <= 1.5 * y[i]

    # calorie band (reasonable)
    prob += T_cal >= target_cal * 0.90
    prob += T_cal <= target_cal * 1.10

    # minimum fiber (relaxed)
    prob += T_fib >= macro_target["fiber_g"] * 0.30

    prob += lpSum(y[i] for i in range(n)) >= min_items
    prob += lpSum(y[i] for i in range(n)) <= max_items

    # deviation vars
    cal_o  = LpVariable("cal_o",  lowBound=0)
    cal_u  = LpVariable("cal_u",  lowBound=0)
    pro_o  = LpVariable("pro_o",  lowBound=0)
    pro_u  = LpVariable("pro_u",  lowBound=0)
    fat_o  = LpVariable("fat_o",  lowBound=0)
    fat_u  = LpVariable("fat_u",  lowBound=0)
    carb_o = LpVariable("carb_o", lowBound=0)
    carb_u = LpVariable("carb_u", lowBound=0)
    fib_u  = LpVariable("fib_u",  lowBound=0)

    prob += T_cal  == float(target_cal)                + cal_o  - cal_u
    prob += T_pro  == float(macro_target["protein_g"]) + pro_o  - pro_u
    prob += T_fat  == float(macro_target["fat_g"])     + fat_o  - fat_u
    prob += T_carb == float(macro_target["carbs_g"])   + carb_o - carb_u
    prob += T_fib  == float(macro_target["fiber_g"])   + 0      - fib_u

    # objective weights
    prob += (
        1.0 * (cal_o  + cal_u) +
        1.1 * (carb_o + carb_u) +
        1.5 * (pro_o  + pro_u) +
        0.7 * (fat_o  + fat_u) +
        1.0 * fib_u
    )

    prob.solve(solver)
    if LpStatus[prob.status] != "Optimal":
        return None

    result = []
    for i in range(n):
        portions = value(x[i])
        if portions is None or portions < 0.01:
            continue

        r = rows.iloc[i]
        grams = float(r["grams_per_portion"]) * float(portions)
        sc = grams / 100.0

        result.append({
            "food_id":      str(r["food_id"]),
            "food_name":    str(r["food_name"]),
            "portions":     round(float(portions), 2),
            "portion_unit": str(r.get("portion_unit", "portion")),
            "grams":        round(grams, 1),
            "calories":     round(float(r["calories"]) * sc, 1),
            "protein":      round(float(r["protein"])  * sc, 1),
            "fat":          round(float(r["fat"])      * sc, 1),
            "carbs":        round(float(r["carbs"])    * sc, 1),
            "fiber":        round(float(r.get("fiber", 0.0)) * sc, 1),
        })

    return result if result else None


# ---------------------------
# full day builder
# ---------------------------

def build_day(
    foods_df: pd.DataFrame,
    targets: dict,
    allergies=None,
    conditions=None,
):
    allergies = allergies or []
    conditions = conditions or []

    foods_df = _ensure_required_cols(foods_df)
    filtered = filter_by_user(foods_df, allergies, conditions)

    total_cal = float(targets.get("calories", targets.get("calories_kcal", 0.0)))

    plan = {"meals": {}, "totals": {}, "warnings": []}
    used_ids = set()
    grand = {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "fiber": 0.0}

    for slot, (cal_frac, min_i, max_i, pool_name) in MEAL_CONFIG.items():
        meal_cal = total_cal * cal_frac

        macro = {
            "protein_g": float(targets["protein_g"]) * cal_frac,
            "fat_g":     float(targets["fat_g"])     * cal_frac,
            "carbs_g":   float(targets["carbs_g"])   * cal_frac,
            "fiber_g":   float(targets["fiber_g"])   * cal_frac,
        }

        pool = get_pool(filtered, pool_name, max_candidates=250)
        pool = pool[~pool["food_id"].isin(used_ids)].reset_index(drop=True)

        if pool.empty:
            plan["meals"][slot] = []
            plan["warnings"].append(f"⚠️ {slot}: EMPTY_POOL")
            continue

        items = solve_one_meal(pool, meal_cal, macro, max_items=max_i, min_items=min_i)

        if items is None:
            plan["meals"][slot] = []
            plan["warnings"].append(f"⚠️ {slot}: INFEASIBLE")
            continue

        for it in items:
            used_ids.add(it["food_id"])
            grand["calories"] += float(it["calories"])
            grand["protein"]  += float(it["protein"])
            grand["fat"]      += float(it["fat"])
            grand["carbs"]    += float(it["carbs"])
            grand["fiber"]    += float(it["fiber"])

        plan["meals"][slot] = items

    plan["totals"] = {k: round(v, 2) for k, v in grand.items()}
    return plan
