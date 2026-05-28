from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional


class NutritionCreateRequest(BaseModel):
    raw_text: str = Field(..., description="Свободный текст питания от пользователя")
    intake_date: Optional[date] = Field(None, description="Дата приёма пищи (по умолчанию сегодня)")


class WorkoutCreateRequest(BaseModel):
    raw_text: str = Field(..., description="Свободный текст тренировки от пользователя")
    workout_date: Optional[date] = Field(None, description="Дата тренировки (по умолчанию сегодня)")


class NutritionSaveResponse(BaseModel):
    success: bool
    intake_id: int
    date: date


class WorkoutSaveResponse(BaseModel):
    success: bool
    workout_id: int
    date: date


class NutritionItem(BaseModel):
    product_name: str
    grams: float
    calories: float
    protein: float
    fat: float
    carbs: float


class NutritionResponse(BaseModel):
    success: bool
    items: Optional[List[NutritionItem]] = None
    error_message: Optional[str] = None


class ExerciseSet(BaseModel):
    weight_kg: Optional[float] = None
    reps: Optional[int] = None
    duration_seconds: Optional[int] = None
    distance_km: Optional[float] = None
    feeling: Optional[str] = None


class Exercise(BaseModel):
    exercise_name: str
    exercise_type: str
    muscle_group: Optional[str] = None
    sets: List[ExerciseSet]
    raw_input_text: Optional[str] = None


class TrainingParseResponse(BaseModel):
    success: bool
    exercises: Optional[List[Exercise]] = None
    error_message: Optional[str] = None


class DailyWorkoutSummary(BaseModel):
    date: date
    exercises: List[str] = Field(..., description="Список названий упражнений в этот день")


class ExercisePeriodStats(BaseModel):
    exercise_name: str
    muscle_group: Optional[str] = None
    total_sets: int
    avg_sets_per_workout: float
    max_weight_kg: Optional[float] = None
    avg_weight_kg: Optional[float] = None
    max_duration_seconds: Optional[int] = None
    avg_duration_seconds: Optional[float] = None
    max_distance_km: Optional[float] = None
    avg_distance_km: Optional[float] = None


class WorkoutPeriodStats(BaseModel):
    start_date: date
    end_date: date
    period_days: int
    total_workouts: int
    exercise_stats: List[ExercisePeriodStats]
    daily_summaries: List[DailyWorkoutSummary]


class DailyNutritionSummary(BaseModel):
    date: date
    calories: float
    protein: float
    fat: float
    carbs: float


class NutritionPeriodStats(BaseModel):
    start_date: date
    end_date: date
    period_days: int
    avg_calories: float
    avg_protein: float
    avg_fat: float
    avg_carbs: float
    daily_summaries: List[DailyNutritionSummary]


class CombinedStatsResponse(BaseModel):
    """Обёртка для возврата полной статистики. Совпадает с RecommendationRequest."""
    workouts: WorkoutPeriodStats
    nutrition: NutritionPeriodStats
