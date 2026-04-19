from db.mongo_handler import (insert_submission,
    get_all_by_student, get_faculty_summary)

# Insert a test record
insert_submission({
    'student_id':    'TEST001',
    'sleep_hours':   5.0,
    'study_hours':   9.0,
    'burnout_score': 0.78,
    'risk_label':    'High',
})
print("Inserted. Check MongoDB Compass.")

# Query it back
df = get_all_by_student('TEST001')
print("Retrieved:")
print(df)

# Summary
summary = get_faculty_summary()
print("\nFaculty summary:")
print(summary)
