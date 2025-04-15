import os
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from loggers import get_logger

# Set up logger
logger = get_logger("database")

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')
logger.info(f"Connecting to database at {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'DATABASE_URL'}")

# Create engine
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Define models
class Survey(Base):
    """Model for survey responses"""
    __tablename__ = 'surveys'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    level_of_study = Column(String(50))
    faculty = Column(String(50))
    ai_familiarity = Column(String(50))
    used_ai_tools = Column(String(255))
    tools_used = Column(String(255))
    usage_frequency = Column(Integer)
    challenges = Column(Text)
    helpful_tools_needed = Column(String(255))
    improves_learning = Column(String(10))
    suggestions = Column(Text)
    tools_count = Column(Integer)
    challenges_count = Column(Integer)
    
    # Relationship with predictions
    predictions = relationship("Prediction", back_populates="survey")
    
    def __repr__(self):
        return f"<Survey(email='{self.email}', faculty='{self.faculty}')>"


class Prediction(Base):
    """Model for AI adoption predictions"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'))
    adoption_probability = Column(Float)
    model_version = Column(String(50))
    created_at = Column(String(50), default=func.now())
    
    # Relationship with survey
    survey = relationship("Survey", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(survey_id={self.survey_id}, adoption_probability={self.adoption_probability})>"


class Insight(Base):
    """Model for AI-generated insights"""
    __tablename__ = 'insights'
    
    id = Column(Integer, primary_key=True)
    batch_id = Column(String(50))
    insight_text = Column(Text)
    category = Column(String(50))
    created_at = Column(String(50), default=func.now())
    
    def __repr__(self):
        return f"<Insight(id={self.id}, category='{self.category}')>"


# Create tables
def init_db():
    """Initialize the database tables"""
    Base.metadata.create_all(engine)


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Helper functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def load_survey_data_to_db(df, db_session=None):
    """
    Load survey data from pandas DataFrame to database
    
    Args:
        df (pd.DataFrame): Processed survey data
        db_session: SQLAlchemy session (optional)
        
    Returns:
        int: Number of records added
    """
    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True
    
    count = 0
    
    try:
        # Convert DataFrame to database records
        for _, row in df.iterrows():
            # Check if email already exists
            existing = db_session.query(Survey).filter_by(email=row['1. Email']).first()
            if existing:
                continue
                
            survey = Survey(
                email=row['1. Email'],
                level_of_study=row['2. Level of study'],
                faculty=row['3. Faculty'],
                ai_familiarity=row['4. AI familiarity'],
                used_ai_tools=row['5. Used AI tools'],
                tools_used=row['6. Tools used'],
                usage_frequency=int(row['7. Usage frequency']),
                challenges=row['8. Challenges'],
                helpful_tools_needed=row['9. Helpful tools needed'],
                improves_learning=row['10. Improves learning?'],
                suggestions=row['11. Suggestions'],
                tools_count=row['tools_count'] if 'tools_count' in row else 0,
                challenges_count=row['challenges_count'] if 'challenges_count' in row else 0
            )
            
            db_session.add(survey)
            count += 1
            
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        if close_session:
            db_session.close()
    
    return count


def save_predictions_to_db(data, predictions, model_version="v1.0", db_session=None):
    """
    Save model predictions to database
    
    Args:
        data (pd.DataFrame): Processed survey data with emails
        predictions (array): Model predictions
        model_version (str): Version of the model
        db_session: SQLAlchemy session (optional)
        
    Returns:
        int: Number of predictions saved
    """
    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True
    
    count = 0
    
    try:
        for i, pred in enumerate(predictions):
            email = data.iloc[i]['1. Email']
            
            # Get survey record
            survey = db_session.query(Survey).filter_by(email=email).first()
            if not survey:
                continue
                
            # Create prediction record
            prediction = Prediction(
                survey_id=survey.id,
                adoption_probability=float(pred),
                model_version=model_version
            )
            
            db_session.add(prediction)
            count += 1
            
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        if close_session:
            db_session.close()
    
    return count


def save_insight_to_db(insight_text, category="general", batch_id=None, db_session=None):
    """
    Save AI-generated insight to database
    
    Args:
        insight_text (str): The generated insight text
        category (str): Category of the insight
        batch_id (str): Batch identifier for grouped insights
        db_session: SQLAlchemy session (optional)
        
    Returns:
        Insight: The created insight object
    """
    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True
    
    try:
        # Create insight record
        insight = Insight(
            insight_text=insight_text,
            category=category,
            batch_id=batch_id or "default"
        )
        
        db_session.add(insight)
        db_session.commit()
        db_session.refresh(insight)
        return insight
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        if close_session:
            db_session.close()


def get_surveys_from_db(limit=None, db_session=None):
    """
    Get survey data from database
    
    Args:
        limit (int, optional): Limit number of records
        db_session: SQLAlchemy session (optional)
        
    Returns:
        list: List of Survey objects
    """
    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True
    
    try:
        query = db_session.query(Survey)
        if limit:
            query = query.limit(limit)
        return query.all()
    finally:
        if close_session:
            db_session.close()


def surveys_to_dataframe(surveys):
    """
    Convert survey objects to pandas DataFrame
    
    Args:
        surveys (list): List of Survey objects
        
    Returns:
        pd.DataFrame: DataFrame with survey data
    """
    data = []
    
    for survey in surveys:
        data.append({
            "1. Email": survey.email,
            "2. Level of study": survey.level_of_study,
            "3. Faculty": survey.faculty,
            "4. AI familiarity": survey.ai_familiarity,
            "5. Used AI tools": survey.used_ai_tools,
            "6. Tools used": survey.tools_used,
            "7. Usage frequency": survey.usage_frequency,
            "8. Challenges": survey.challenges,
            "9. Helpful tools needed": survey.helpful_tools_needed,
            "10. Improves learning?": survey.improves_learning,
            "11. Suggestions": survey.suggestions,
            "tools_count": survey.tools_count,
            "challenges_count": survey.challenges_count
        })
    
    return pd.DataFrame(data)


# Initialize database if this script is run directly
if __name__ == "__main__":
    init_db()