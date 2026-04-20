
from db.models import BurnoutSubmission, init_db
from datetime import datetime
import pandas as pd

_db_initialized = False

def _get_connection():
    """Initialize MongoDB connection (lazy initialization)."""
    global _db_initialized
    if not _db_initialized:
        try:
            init_db()
            _db_initialized = True
        except ConnectionError as e:
            raise e
    return True

def insert_submission(form_dict: dict) -> str:
    """Insert a new burnout submission using MongoEngine."""
    try:
        _get_connection()
        
        # Create submission document
        submission = BurnoutSubmission(
            student_id=form_dict.get('student_id', 'Unknown'),
            age=form_dict.get('age', 0),
            gender=form_dict.get('gender', ''),
            course=form_dict.get('course', ''),
            semester=form_dict.get('semester', 0),
            study_hours=form_dict.get('study_hours', 0),
            sleep_hours=form_dict.get('sleep_hours', 0),
            assign_pressure=form_dict.get('assign_pressure', 0),
            exam_pressure=form_dict.get('exam_pressure', 0),
            attend_stress=form_dict.get('attend_stress', 0),
            screen_time=form_dict.get('screen_time', 0),
            stress_level=form_dict.get('stress_level', 0),
            anxiety_level=form_dict.get('anxiety_level', 0),
            exercise_freq=form_dict.get('exercise_freq', ''),
            social_freq=form_dict.get('social_freq', ''),
            emotional_exh=form_dict.get('emotional_exh', ''),
            lost_motiv=form_dict.get('lost_motiv', ''),
            support_level=form_dict.get('support_level', 0),
            mentally_drain=form_dict.get('mentally_drain', ''),
            difficulty_conc=form_dict.get('difficulty_conc', ''),
            burnout_score=form_dict.get('burnout_score', 0.0),
            risk_label=form_dict.get('risk_label', ''),
            confidence=form_dict.get('confidence', 0.0),
            notes=form_dict.get('notes', ''),
            timestamp=datetime.now()
        )
        
        # Save and return ID
        submission.save()
        return str(submission.id)
    except ConnectionError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to insert submission: {str(e)}")

def get_all_by_student(student_id: str) -> pd.DataFrame:
    """Return all submissions for a student, sorted by time (newest first)."""
    try:
        _get_connection()
        submissions = BurnoutSubmission.objects(student_id=student_id).order_by('-timestamp')
        
        if not submissions:
            return pd.DataFrame()
        
        data = [sub.to_dict() for sub in submissions]
        df = pd.DataFrame(data)
        return df
    except ConnectionError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to fetch student submissions: {str(e)}")

def get_faculty_summary() -> pd.DataFrame:
    """Aggregate: average burnout per student, sorted by average burnout descending."""
    try:
        _get_connection()
        
        # Use MongoDB aggregation through MongoEngine
        pipeline = [
            {'$group': {
                '_id': '$student_id',
                'avg_burnout': {'$avg': '$burnout_score'},
                'submissions': {'$sum': 1}
            }},
            {'$sort': {'avg_burnout': -1}}
        ]
        
        results = BurnoutSubmission.objects.aggregate(*pipeline)
        data = list(results)
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df.rename(columns={'_id': 'student_id'}, inplace=True)
        return df
    except ConnectionError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to fetch faculty summary: {str(e)}")

def get_recent_n(n=50) -> pd.DataFrame:
    """Get the n most recent submissions."""
    try:
        _get_connection()
        submissions = BurnoutSubmission.objects.order_by('-timestamp').limit(n)
        
        if not submissions:
            return pd.DataFrame()
        
        data = [sub.to_dict() for sub in submissions]
        df = pd.DataFrame(data)
        return df
    except ConnectionError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to fetch recent submissions: {str(e)}")

def get_all_students() -> list:
    """Get list of all unique student IDs."""
    try:
        _get_connection()
        students = BurnoutSubmission.objects.distinct('student_id')
        return sorted(students)
    except ConnectionError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to fetch students: {str(e)}")

def get_latest_by_student(student_id: str) -> dict:
    """Get the most recent submission for a student."""
    try:
        _get_connection()
        submission = BurnoutSubmission.objects(student_id=student_id).order_by('-timestamp').first()
        
        if not submission:
            return None
        
        return submission.to_dict()
    except ConnectionError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to fetch latest submission: {str(e)}")

def get_all_latest() -> pd.DataFrame:
    """Get latest submission for each student."""
    try:
        _get_connection()
        
        # Use MongoDB aggregation to get latest per student
        pipeline = [
            {'$sort': {'timestamp': -1}},
            {'$group': {
                '_id': '$student_id',
                'student_id': {'$first': '$student_id'},
                'burnout_score': {'$first': '$burnout_score'},
                'risk_label': {'$first': '$risk_label'},
                'confidence': {'$first': '$confidence'},
                'timestamp': {'$first': '$timestamp'}
            }},
            {'$sort': {'burnout_score': -1}}
        ]
        
        results = BurnoutSubmission.objects.aggregate(*pipeline)
        data = list(results)
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        # Clean up _id field if it exists
        if '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)
        
        return df
    except ConnectionError as e:
        raise e
    except Exception as e:
        raise Exception(f"Failed to fetch latest submissions: {str(e)}")

