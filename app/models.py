from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    workout_date = Column(Date, nullable=False)
    raw_input_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    exercise_logs = relationship("ExerciseLog", back_populates="workout")


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="CASCADE"))
    user_id = Column(Integer, nullable=False)
    exercise_name = Column(String(255), nullable=False)
    exercise_type = Column(String(30), nullable=False)
    muscle_group = Column(String(100), nullable=True)
    raw_input_text = Column(Text, nullable=True)

    workout = relationship("Workout", back_populates="exercise_logs")
    sets = relationship("ExerciseSet", back_populates="exercise_log")


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id = Column(Integer, primary_key=True, index=True)
    exercise_log_id = Column(Integer, ForeignKey("exercise_logs.id", ondelete="CASCADE"))
    weight_kg = Column(Float, nullable=True)
    reps = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    distance_km = Column(Float, nullable=True)
    feeling = Column(String(20), nullable=True)


class FoodIntake(Base):
    __tablename__ = "food_intakes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    intake_date = Column(Date, nullable=False)
    raw_text = Column(Text, nullable=False)
    product_name = Column(String(255), nullable=True)
    grams = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)