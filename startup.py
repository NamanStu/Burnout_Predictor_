#!/usr/bin/env python3
"""
Student Burnout Early Warning System - Startup Verification Script
This script verifies all dependencies and starts the GUI application.
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if all required packages are installed"""
    print("="*60)
    print("STUDENT BURNOUT DETECTION SYSTEM - STARTUP CHECK")
    print("="*60)
    
    required_packages = {
        'tkinter': 'Tkinter (GUI Framework)',
        'pandas': 'Pandas (Data Processing)',
        'numpy': 'NumPy (Numerical Computing)',
        'sklearn': 'Scikit-learn (ML Models)',
        'joblib': 'Joblib (Model Serialization)',
        'PIL': 'Pillow (Image Processing)',
        'pymongo': 'PyMongo (MongoDB Driver)',
        'vaderSentiment': 'VADER Sentiment Analysis',
    }
    
    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name:<35} ... OK")
        except ImportError:
            print(f"❌ {name:<35} ... MISSING")
            missing.append(package)
    
    print("\n" + "="*60)
    
    if missing:
        print(f"⚠️  {len(missing)} package(s) missing!")
        print("\nInstall missing packages with:")
        print(f"python3 -m pip install {' '.join(missing)}")
        return False
    else:
        print("✅ All dependencies are installed!")
        return True

def verify_models():
    """Verify that trained models exist"""
    print("\n" + "="*60)
    print("VERIFYING MODEL FILES")
    print("="*60)
    
    required_files = [
        'models/logisticregression.pkl',
        'models/scaler.pkl',
        'models/label_encoder.pkl',
        'models/feature_names.pkl',
        'models/metrics.json',
        'data/X_train.npy',
        'data/X_test.npy',
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
            print(f"✅ {file:<35} ... {size_str}")
        else:
            print(f"❌ {file:<35} ... MISSING")
            all_exist = False
    
    print("\n" + "="*60)
    if not all_exist:
        print("⚠️  Some model files are missing!")
        print("Run preprocessing and training scripts first.")
        return False
    else:
        print("✅ All model files verified!")
        return True

def test_predictor():
    """Quick test of the predictor"""
    print("\n" + "="*60)
    print("TESTING PREDICTOR")
    print("="*60)
    
    try:
        from models.predictor import predict
        
        result = predict({
            'age': 21,
            'gender': 'Male',
            'course': 'BTech',
            'semester': 4,
            'study_hours': 6.0,
            'sleep_hours': 7.0,
            'assignment_pressure': 5,
            'exam_pressure': 5,
            'attendance_stress': 5,
            'screen_time_hours': 5.0,
            'stress_level': 5,
            'anxiety_level': 5,
            'exercise_frequency': '1-2 times/week',
            'socializing_frequency': 'Sometimes',
            'emotionally_exhausted': 'No',
            'lost_motivation': 'No',
            'support_level': 6,
            'mentally_drained_frequency': 'Sometimes',
            'difficulty_concentrating': 'No',
        })
        
        print(f"✅ Prediction successful!")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Risk Label: {result['risk_label']}")
        print(f"   Confidence: {result['confidence']}%")
        return True
    except Exception as e:
        print(f"❌ Predictor test failed: {e}")
        return False

def launch_gui():
    """Launch the GUI application"""
    print("\n" + "="*60)
    print("LAUNCHING GUI APPLICATION")
    print("="*60)
    print("\n✨ Starting Student Burnout Early Warning System...\n")
    print("The GUI window should open shortly.")
    print("If it doesn't appear, check that:")
    print("  • Display/X11 forwarding is properly configured")
    print("  • You're not in a headless environment")
    print("  • Tkinter permissions are correct")
    print("\n" + "="*60 + "\n")
    
    # Launch the main GUI
    subprocess.run([sys.executable, 'main.py'])

if __name__ == '__main__':
    print("\n")
    
    # Run all checks
    deps_ok = check_dependencies()
    models_ok = verify_models()
    predictor_ok = test_predictor()
    
    if deps_ok and models_ok and predictor_ok:
        print("\n✅ All checks passed! System is ready.")
        launch_gui()
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("Try running the setup scripts first:")
        print("  python3 models/preprocess.py")
        print("  python3 models/train_models.py")
        sys.exit(1)
