"""
MongoEngine models for student burnout data
"""
from mongoengine import (
    Document, StringField, IntField, FloatField, 
    DateTimeField, connect, disconnect
)
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path to import config
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Initialize connection (called separately to allow lazy loading)
def init_db(db_name=None, host=None):
    """Initialize MongoDB connection with MongoEngine."""
    try:
        # Use provided parameters or load from config
        if db_name is None or host is None:
            from config import MONGODB_DB_NAME, MONGODB_HOST
            db_name = db_name or MONGODB_DB_NAME
            host = host or MONGODB_HOST
        
        disconnect()  # Disconnect any existing connection
        connect(db_name, host=host, retryWrites=False)
        return True
    except Exception as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

class BurnoutSubmission(Document):
    """
    Model for student burnout assessment submissions.
    
    Fields:
    - student_id: Unique identifier for the student
    - age: Age of student (integer)
    - gender: Gender (Male/Female/Other)
    - course: Course name
    - semester: Current semester (integer)
    - study_hours: Daily study hours (integer)
    - sleep_hours: Daily sleep hours (integer)
    - assign_pressure: Assignment pressure level (1-10)
    - exam_pressure: Exam pressure level (1-10)
    - attend_stress: Attendance stress (1-10)
    - screen_time: Daily screen time (1-10)
    - stress_level: Overall stress level (1-10)
    - anxiety_level: Anxiety level (1-10)
    - exercise_freq: Exercise frequency
    - social_freq: Social activity frequency
    - emotional_exh: Emotional exhaustion (Yes/Sometimes/No)
    - lost_motiv: Lost motivation frequency
    - support_level: Support level (1-10)
    - mentally_drain: Mental drain frequency
    - difficulty_conc: Difficulty concentrating (Yes/Sometimes/No)
    - burnout_score: ML model prediction (0.0-1.0)
    - risk_label: Risk category (High/Medium/Low)
    - confidence: Model confidence (0-100%)
    - notes: Additional notes from student
    - timestamp: Submission timestamp
    """
    
    # Student Information
    student_id = StringField(required=True)
    age = IntField(required=True)
    gender = StringField(required=True)
    course = StringField(required=True)
    semester = IntField(required=True)
    
    # Academic Factors
    study_hours = IntField(required=True)
    sleep_hours = IntField(required=True)
    assign_pressure = IntField(required=True)
    exam_pressure = IntField(required=True)
    attend_stress = IntField(required=True)
    
    # Lifestyle Factors
    screen_time = IntField(required=True)
    stress_level = IntField(required=True)
    anxiety_level = IntField(required=True)
    exercise_freq = StringField(required=True)
    social_freq = StringField(required=True)
    
    # Mental Health Indicators
    emotional_exh = StringField(required=True)
    lost_motiv = StringField(required=True)
    support_level = IntField(required=True)
    mentally_drain = StringField(required=True)
    difficulty_conc = StringField(required=True)
    
    # ML Model Predictions
    burnout_score = FloatField(required=True)
    risk_label = StringField(required=True)
    confidence = FloatField(required=True)
    
    # Additional Info
    notes = StringField(default='')
    timestamp = DateTimeField(default=datetime.now, required=True)
    
    meta = {
        'collection': 'burnout_submissions',
        'indexes': [
            'student_id',
            'timestamp',
            'risk_label',
            'burnout_score'
        ]
    }
    
    def to_dict(self):
        """Convert document to dictionary."""
        return {
            'student_id': self.student_id,
            'age': self.age,
            'gender': self.gender,
            'course': self.course,
            'semester': self.semester,
            'study_hours': self.study_hours,
            'sleep_hours': self.sleep_hours,
            'assign_pressure': self.assign_pressure,
            'exam_pressure': self.exam_pressure,
            'attend_stress': self.attend_stress,
            'screen_time': self.screen_time,
            'stress_level': self.stress_level,
            'anxiety_level': self.anxiety_level,
            'exercise_freq': self.exercise_freq,
            'social_freq': self.social_freq,
            'emotional_exh': self.emotional_exh,
            'lost_motiv': self.lost_motiv,
            'support_level': self.support_level,
            'mentally_drain': self.mentally_drain,
            'difficulty_conc': self.difficulty_conc,
            'burnout_score': self.burnout_score,
            'risk_label': self.risk_label,
            'confidence': self.confidence,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp)
        }
