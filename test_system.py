#!/usr/bin/env python3
"""
System Test for SignalDrop AI
Tests all components and API endpoints to ensure everything works correctly.
"""

import requests
import json
import time
import sys

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get('http://localhost:8001/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend Health Check:")
            print(f"   Status: {data['status']}")
            print(f"   Data Loaded: {data['data_loaded']}")
            print(f"   Students Analyzed: {data['students_analyzed']}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_students_endpoint():
    """Test students endpoint"""
    try:
        response = requests.get('http://localhost:8001/api/students', timeout=5)
        if response.status_code == 200:
            students = response.json()
            print(f"✅ Students Endpoint: Found {len(students)} students")
            for student in students:
                print(f"   {student['student_id']}: {student['risk_level']} risk ({student['risk_score']:.2f})")
            return True
        else:
            print(f"❌ Students endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Students endpoint error: {e}")
        return False

def test_student_detail(student_id):
    """Test student detail endpoint"""
    try:
        response = requests.get(f'http://localhost:8001/api/student/{student_id}', timeout=5)
        if response.status_code == 200:
            detail = response.json()
            print(f"✅ Student Detail ({student_id}):")
            print(f"   Risk Score: {detail['risk_score']:.2f}")
            print(f"   Explanation: {detail['explanation'][:50]}...")
            print(f"   Key Signals: {len(detail['key_signals'])} signals")
            return True
        else:
            print(f"❌ Student detail failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Student detail error: {e}")
        return False

def test_causal_analysis(student_id):
    """Test causal analysis endpoint"""
    try:
        response = requests.get(f'http://localhost:8001/api/student/{student_id}/what-changed', timeout=5)
        if response.status_code == 200:
            analysis = response.json()
            print(f"✅ Causal Analysis ({student_id}):")
            causal = analysis['causal_analysis']
            print(f"   Analysis Period: {causal['analysis_period']}")
            print(f"   Significant Changes: {len(causal['significant_changes'])}")
            return True
        else:
            print(f"❌ Causal analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Causal analysis error: {e}")
        return False

def test_counterfactuals(student_id):
    """Test counterfactuals endpoint"""
    try:
        response = requests.get(f'http://localhost:8001/api/student/{student_id}/counterfactuals', timeout=5)
        if response.status_code == 200:
            counterfactuals = response.json()
            print(f"✅ Counterfactuals ({student_id}):")
            scenarios = counterfactuals['counterfactuals']
            print(f"   Scenarios: {len(scenarios)}")
            return True
        else:
            print(f"❌ Counterfactuals failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Counterfactuals error: {e}")
        return False

def main():
    """Run all system tests"""
    print("🔍 SignalDrop AI - System Test Suite")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ System test failed: Backend not healthy")
        sys.exit(1)
    
    # Test students endpoint
    if not test_students_endpoint():
        print("\n❌ System test failed: Students endpoint")
        sys.exit(1)
    
    # Get a sample student for detailed tests
    try:
        response = requests.get('http://localhost:8001/api/students', timeout=5)
        students = response.json()
        sample_student = students[0]['student_id']
    except:
        print("\n❌ Could not get sample student")
        sys.exit(1)
    
    # Test detailed endpoints
    tests = [
        ("Student Detail", lambda: test_student_detail(sample_student)),
        ("Causal Analysis", lambda: test_causal_analysis(sample_student)),
        ("Counterfactuals", lambda: test_counterfactuals(sample_student)),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        time.sleep(0.5)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All system tests passed! SignalDrop AI is fully operational.")
        print("\n🚀 Access Points:")
        print("   Backend API: http://localhost:8001")
        print("   Frontend Dashboard: http://localhost:3001")
        print("   API Documentation: http://localhost:8001/docs")
        return True
    else:
        print(f"❌ {len(tests) - passed} tests failed. System needs attention.")
        return False

if __name__ == "__main__":
    main()
