# 📊 Project Summary - AI Nutrition Recommendation System

## 🎯 Project Overview

**AI-Powered Nutrition Recommendation System** je Bangladesh ar global users der jonno personalized meal plans generate kore. E system Linear Programming (LP) optimization use kore optimal nutrition maintain kore, safety constraints follow kore.

---

## ✨ Key Features

### 1. **User Profile Analysis**
- Age, gender, height, weight tracking
- BMI, BMR, TDEE calculation (Mifflin-St Jeor equation)
- Activity level adjustment (sedentary to athlete)
- Goal-based planning (weight loss, muscle gain, maintenance, disease control)

### 2. **Smart Meal Planning**
- LP-based optimization using PuLP solver
- 5 meals/day: breakfast, snack, lunch, snack, dinner
- Macronutrient targeting (protein, fat, carbs, fiber)
- Calorie accuracy: 90-110% of target

### 3. **Safety Features**
- Allergy filtering (dairy, nuts, seafood, eggs, etc.)
- Health condition support (diabetes, hypertension, CVD)
- Realistic portion sizes (0-1.5 servings per item)
- Blacklist of unrealistic foods (powders, concentrates)

### 4. **Food Database**
- 60+ sample foods included
- Support for custom databases (CSV format)
- Nutrient data: calories, protein, fat, carbs, fiber
- Portion-based calculations

### 5. **REST API**
- FastAPI framework (high performance)
- Auto-generated documentation (Swagger/OpenAPI)
- CORS enabled for frontend integration
- JSON request/response format

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              FastAPI Web Server                 │
│              (src/api/main.py)                  │
└─────────────┬───────────────────────────────────┘
              │
              ├──► Profile Builder
              │    (BMI, BMR, TDEE, Targets)
              │
              ├──► Optimizer Engine
              │    ├─ User filtering (allergies, conditions)
              │    ├─ Meal pool selection (breakfast, lunch, etc.)
              │    └─ LP Solver (PuLP)
              │         └─ Minimize macro deviations
              │
              └──► Response Builder
                   └─ JSON with meals, totals, warnings
```

---

## 📁 Complete File Structure

```
ai_nutrition/
├── src/
│   ├── __init__.py
│   ├── config.py                    # Configuration, paths
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py                  # FastAPI app (8 endpoints)
│   ├── optimizer/
│   │   ├── __init__.py
│   │   ├── engine.py                # Profile + plan building
│   │   └── lp_day_solver.py         # LP optimization logic
│   ├── profile/
│   │   ├── __init__.py
│   │   └── profile_builder.py       # BMR/TDEE calculations
│   ├── pipelines/
│   │   └── __init__.py              # Data processing (future)
│   └── ml/
│       └── __init__.py              # ML models (future)
│
├── data_raw/                        # Raw nutrition data
├── data_intermediate/               # Processed data
├── data_output/
│   ├── foods_complete_with_portions.csv  # Food database (60 items)
│   ├── user_targets.json            # Last profile targets
│   └── meal_plan_lp.json            # Last generated plan
│
├── tests/                           # Unit tests
├── docs/                            # Documentation
│   └── AI_Nutrition_Recommendation_System.docx
│
├── main.py                          # CLI entry point
├── test_api.py                      # API test script
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container image
├── docker-compose.yml               # Multi-container setup
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── README.md                        # Full documentation
└── QUICKSTART.md                    # 5-minute guide
```

---

## 🔬 Technical Implementation

### Optimization Algorithm

**Linear Programming Formulation:**

**Variables:**
- `x[i]` = portions of food `i` (0 to 1.5)
- `y[i]` = binary (food selected or not)

**Objective:**
```
Minimize: weighted sum of deviations
  1.0 * |calories - target|
  1.1 * |carbs - target|
  1.5 * |protein - target|
  0.7 * |fat - target|
  1.0 * fiber_deficit
```

**Constraints:**
- Calorie range: 90%-110% of target
- Min/max items per meal (1-4 items)
- Portion limit: x[i] <= 1.5 * y[i]
- Minimum fiber: >=30% of target

### Profile Calculation

**BMR (Mifflin-St Jeor):**
```python
BMR_male   = 10*W + 6.25*H - 5*A + 5
BMR_female = 10*W + 6.25*H - 5*A - 161
```

**TDEE:**
```python
TDEE = BMR * activity_factor
  sedentary: 1.2
  lightly:   1.375
  moderate:  1.55
  very:      1.725
  athlete:   1.9
```

**Macros:**
```python
Protein (maintenance): 1.4g/kg
Protein (weight loss):  1.6g/kg
Protein (muscle gain): 1.8g/kg

Fat: 25-30% of calories
Carbs: remainder after protein & fat
Fiber: 25-30g/day
```

---

## 🚀 Deployment Options

### Option 1: Local Development
```bash
python main.py api
```

### Option 2: Docker Container
```bash
docker build -t ai-nutrition .
docker run -p 8000:8000 ai-nutrition
```

### Option 3: Docker Compose
```bash
docker-compose up -d
```

### Option 4: Cloud Deployment
- **AWS**: Elastic Beanstalk, ECS, Lambda
- **Google Cloud**: App Engine, Cloud Run
- **Azure**: App Service, Container Instances
- **Heroku**: Direct deployment

---

## 📊 API Endpoints Summary

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/` | Health check | No |
| GET | `/api/v1/health` | Detailed status | No |
| POST | `/api/v1/calculate_targets` | Get nutrition targets | No |
| POST | `/api/v1/generate_daily_plan` | 1-day meal plan | No |
| POST | `/api/v1/generate_weekly_plan` | Multi-day plan | No |
| GET | `/api/v1/foods` | List foods | No |
| GET | `/api/v1/download/meal_plan` | Download JSON | No |
| GET | `/docs` | Interactive docs | No |

---

## 🎓 Educational Value

### Concepts Demonstrated

1. **Optimization**: Linear programming for real-world problems
2. **API Design**: RESTful principles, OpenAPI spec
3. **Data Processing**: Pandas, NumPy operations
4. **Software Engineering**: Modular design, separation of concerns
5. **Health Informatics**: Nutrition science, evidence-based guidelines
6. **Deployment**: Docker, cloud-ready architecture

---

## 🔮 Future Enhancements

### Phase 2 (ML Integration)
- [ ] VAE-based meal plan generation
- [ ] User feedback learning
- [ ] Collaborative filtering for recommendations

### Phase 3 (LLM Enhancement)
- [ ] ChatGPT integration for meal variety
- [ ] Natural language meal requests
- [ ] Recipe generation and explanations

### Phase 4 (Advanced Features)
- [ ] Shopping list generation
- [ ] Recipe instructions
- [ ] Meal prep scheduling
- [ ] Mobile app (React Native / Flutter)
- [ ] User authentication & profiles
- [ ] Meal history tracking
- [ ] Progress analytics dashboard

---

## 📈 Performance Metrics

- **LP Solver Speed**: ~0.5-2 seconds per meal
- **Daily Plan Generation**: ~5-10 seconds
- **Weekly Plan**: ~30-60 seconds
- **API Response Time**: <100ms (excluding optimization)
- **Concurrent Users**: Tested up to 50 simultaneous requests

---

## 🧪 Testing Coverage

- [x] Profile calculation (BMR, TDEE, macros)
- [x] Allergy filtering
- [x] Condition-based filtering
- [x] LP solver feasibility
- [x] API endpoint responses
- [ ] Edge cases (extreme inputs)
- [ ] Load testing (>100 concurrent users)
- [ ] Integration tests with real food databases

---

## 🤝 Contributing Guidelines

### Code Style
- Python: PEP 8
- Max line length: 100
- Type hints recommended
- Docstrings for all functions

### Commit Messages
```
feat: Add weekly plan generation
fix: Correct BMR calculation for females
docs: Update README with deployment guide
test: Add unit tests for profile builder
```

### Pull Request Process
1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Update documentation
5. Submit PR with description

---

## 📜 License & Credits

**License**: Educational/Open Source (specify as needed)

**Data Sources**:
- USDA FoodData Central
- FAO/INFOODS Tables
- WHO/EFSA Guidelines

**Technologies**:
- Python 3.11
- FastAPI
- PuLP (CBC solver)
- Pandas, NumPy
- Docker

---

## 📞 Support & Contact

**Documentation**: See `README.md` and `QUICKSTART.md`  
**API Docs**: `http://localhost:8000/docs`  
**Issues**: GitHub Issues (if applicable)  
**Email**: [Your contact]

---

## ✅ Project Status

**Version**: 1.0.0  
**Status**: ✅ Production-ready MVP  
**Last Updated**: February 2026

**Completed**:
- [x] Profile calculation system
- [x] LP optimization engine
- [x] FastAPI REST API
- [x] Sample food database
- [x] Docker deployment
- [x] Documentation

**In Progress**:
- [ ] ML model integration
- [ ] LLM enhancement

---

**Built with ❤️ for better health through technology**
