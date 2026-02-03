"""
Simple test client for the AI Nutrition API
"""
import requests
import json
from datetime import date

# API base URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    print(f"✅ Status: {data['status']}")
    print(f"📊 Foods loaded: {data['foods_loaded']}")
    return response.status_code == 200


def test_calculate_targets():
    """Test target calculation"""
    print("\n🎯 Testing target calculation...")
    
    profile = {
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
    
    response = requests.post(
        f"{BASE_URL}/api/v1/calculate_targets",
        json=profile
    )
    
    if response.status_code == 200:
        data = response.json()
        targets = data['profile']['targets']
        metrics = data['profile']['metrics']
        
        print(f"✅ BMI: {metrics['bmi']}")
        print(f"✅ TDEE: {metrics['tdee_kcal']} kcal")
        print(f"✅ Target Calories: {targets['calories']} kcal")
        print(f"✅ Protein: {targets['protein_g']}g")
        print(f"✅ Fat: {targets['fat_g']}g")
        print(f"✅ Carbs: {targets['carbs_g']}g")
        print(f"✅ Fiber: {targets['fiber_g']}g")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False


def test_generate_daily_plan():
    """Test daily plan generation"""
    print("\n🍽️ Testing daily plan generation...")
    
    profile = {
        "age": 25,
        "gender": "female",
        "height_cm": 165,
        "weight_kg": 60,
        "activity": "moderate",
        "goal": "weight_loss",
        "intensity": "standard",
        "conditions": [],
        "allergies": ["dairy"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate_daily_plan",
        json=profile
    )
    
    if response.status_code == 200:
        data = response.json()
        plan = data['plan']
        
        print(f"✅ Date: {data['date']}")
        print(f"\n📊 Daily Totals:")
        for nutrient, value in plan['totals'].items():
            print(f"   {nutrient}: {value}")
        
        print(f"\n🍴 Meals:")
        for meal_name, items in plan['meals'].items():
            print(f"\n   {meal_name.upper()}: ({len(items)} items)")
            for item in items:
                print(f"      • {item['food_name']} - {item['portions']} {item['portion_unit']} ({item['grams']}g)")
                print(f"        Cal: {item['calories']} | P: {item['protein']}g | F: {item['fat']}g | C: {item['carbs']}g")
        
        if plan.get('warnings'):
            print(f"\n⚠️ Warnings:")
            for warning in plan['warnings']:
                print(f"   {warning}")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False


def test_weekly_plan():
    """Test weekly plan generation"""
    print("\n📅 Testing weekly plan generation...")
    
    request_data = {
        "profile": {
            "age": 30,
            "gender": "male",
            "height_cm": 175,
            "weight_kg": 75,
            "activity": "moderate",
            "goal": "muscle_gain",
            "intensity": "standard",
            "conditions": [],
            "allergies": []
        },
        "days": 3  # Test with 3 days for speed
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate_weekly_plan",
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        weekly = data['weekly_plan']
        
        print(f"✅ Generated {len(weekly['days'])} days")
        print(f"\n📊 Weekly Averages:")
        for nutrient, value in weekly['daily_averages'].items():
            print(f"   {nutrient}: {value}")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False


def main():
    """Run all tests"""
    print("🧪 AI Nutrition API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Calculate Targets", test_calculate_targets),
        ("Generate Daily Plan", test_generate_daily_plan),
        ("Generate Weekly Plan", test_weekly_plan),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n🎯 Total: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
