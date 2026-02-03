# 🚀 Quick Start Guide

## 5-Minute Setup & Test

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start the API

```bash
python main.py api
```

The API will start on `http://localhost:8000`

### Step 3: Open Interactive Docs

Open your browser and go to:
```
http://localhost:8000/docs
```

### Step 4: Test with Sample Requests

#### Option A: Use the Interactive Docs (Recommended)

1. Click on `/api/v1/generate_daily_plan`
2. Click "Try it out"
3. Use this sample JSON:

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

4. Click "Execute"
5. See your meal plan!

#### Option B: Use Python Script

```bash
# Open a new terminal (keep the API running)
python test_api.py
```

#### Option C: Use cURL

```bash
curl -X POST "http://localhost:8000/api/v1/generate_daily_plan" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 25,
    "gender": "female",
    "height_cm": 165,
    "weight_kg": 60,
    "activity": "moderate",
    "goal": "weight_loss",
    "intensity": "standard",
    "conditions": [],
    "allergies": ["dairy"]
  }'
```

---

## Common Test Scenarios

### 1. Weight Loss Plan (Female)
```json
{
  "age": 25,
  "gender": "female",
  "height_cm": 165,
  "weight_kg": 70,
  "activity": "lightly",
  "goal": "weight_loss",
  "intensity": "standard",
  "allergies": []
}
```

### 2. Muscle Gain Plan (Male)
```json
{
  "age": 28,
  "gender": "male",
  "height_cm": 180,
  "weight_kg": 75,
  "activity": "very",
  "goal": "muscle_gain",
  "intensity": "standard",
  "allergies": []
}
```

### 3. Diabetes Control
```json
{
  "age": 50,
  "gender": "male",
  "height_cm": 170,
  "weight_kg": 85,
  "activity": "moderate",
  "goal": "diabetes_control",
  "conditions": ["diabetes"],
  "allergies": []
}
```

### 4. With Allergies
```json
{
  "age": 30,
  "gender": "female",
  "height_cm": 165,
  "weight_kg": 60,
  "activity": "moderate",
  "goal": "maintain",
  "allergies": ["dairy", "seafood"]
}
```

---

## API Endpoints Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/v1/calculate_targets` | POST | Get nutritional targets only |
| `/api/v1/generate_daily_plan` | POST | Generate 1-day meal plan |
| `/api/v1/generate_weekly_plan` | POST | Generate multi-day plan |
| `/api/v1/foods` | GET | List available foods |
| `/docs` | GET | Interactive API documentation |

---

## Troubleshooting

### API won't start?

```bash
# Check if port 8000 is in use
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# Use a different port
python main.py api --port 8080
```

### "Food database not available"?

✅ Already fixed! The project includes a sample database with 60 foods.

### Import errors?

```bash
# Make sure you're in the project root
cd /path/to/ai_nutrition

# Run from there
python main.py api
```

---

## Next Steps

1. ✅ Test the API with sample requests
2. 📊 Add your own food database (see README.md)
3. 🔧 Customize meal rules in `src/optimizer/lp_day_solver.py`
4. 🌐 Build a frontend (React, Vue, etc.)
5. 📱 Create a mobile app

---

## Need Help?

- Check `README.md` for detailed documentation
- Visit `http://localhost:8000/docs` for interactive API docs
- Review `test_api.py` for example code

**Happy meal planning! 🍎**
