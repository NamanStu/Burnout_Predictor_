from models.predictor import predict

# High-stress student (High burnout risk)
result = predict({
    'age': 22,
    'gender': 'Male',
    'course': 'BTech',
    'semester': 6,
    'study_hours': 10.0,
    'sleep_hours': 3.5,
    'assignment_pressure': 9,
    'exam_pressure': 9,
    'attendance_stress': 10,
    'screen_time_hours': 3.6,
    'stress_level': 10,
    'anxiety_level': 9,
    'exercise_frequency': 'Never',
    'socializing_frequency': 'Sometimes',
    'emotionally_exhausted': 'Yes',
    'lost_motivation': 'Sometimes',
    'support_level': 5,
    'mentally_drained_frequency': 'Often',
    'difficulty_concentrating': 'Sometimes',
})
print("HIGH BURNOUT RISK TEST:")
print(f"  Score:      {result['score']}")
print(f"  Risk:       {result['risk_label']}")
print(f"  Confidence: {result['confidence']}%")
print(f"  SHAP saved: {result['shap_path']}")

# Low-stress student (Low burnout risk)
result2 = predict({
    'age': 21,
    'gender': 'Female',
    'course': 'BCom',
    'semester': 4,
    'study_hours': 3.9,
    'sleep_hours': 7.6,
    'assignment_pressure': 3,
    'exam_pressure': 2,
    'attendance_stress': 2,
    'screen_time_hours': 8.2,
    'stress_level': 3,
    'anxiety_level': 4,
    'exercise_frequency': 'Daily',
    'socializing_frequency': 'Sometimes',
    'emotionally_exhausted': 'No',
    'lost_motivation': 'No',
    'support_level': 8,
    'mentally_drained_frequency': 'Never',
    'difficulty_concentrating': 'Sometimes',
})
print("\nLOW BURNOUT RISK TEST:")
print(f"  Score:      {result2['score']}")
print(f"  Risk:       {result2['risk_label']}")
print(f"  Confidence: {result2['confidence']}%")
