from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional


class FoodCreate(BaseModel):
    """
    Запрос на добавление записи о питании.
    Принимает весь текст, который ввёл пользователь.
    """
    raw_text: str = Field(
        ...,
        description="Полный текст питания от пользователя (например: 'курица 200г, рис 150г, борщ 400г')"
    )
    intake_date: Optional[date] = Field(
        None,
        description="Дата приёма пищи (если не указана — используется текущая)"
    )


class FoodItemResponse(BaseModel):
    """
    Информация по одному продукту после обработки.
    """
    product_name: str
    grams: float
    calories: float
    protein: float
    fat: float
    carbs: float


class FoodResponse(BaseModel):
    """
    Ответ после обработки питания.
    """
    success: bool
    items: Optional[List[FoodItemResponse]] = Field(None, description="Список обработанных продуктов")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке, если что-то пошло не так")
    fallback_used: bool = Field(False, description="True, если использовалась нейросеть (fallback)")


class ExerciseSetCreate(BaseModel):
    """
    Один подход в упражнении.
    """
    weight_kg: Optional[float] = Field(None, description="Вес в килограммах")
    reps: Optional[int] = Field(None, description="Количество повторений")
    duration_seconds: Optional[int] = Field(None, description="Время в секундах")
    distance_km: Optional[float] = Field(None, description="Дистанция в километрах")
    feeling: Optional[str] = Field(None, description="Субъективное ощущение")


class ExerciseCreate(BaseModel):
    """
    Одно упражнение (может содержать несколько подходов).
    """
    exercise_name: str = Field(..., description="Название упражнения")
    exercise_type: str = Field(..., description="Тип упражнения: weight_reps, bodyweight_reps, timed, cardio_distance, other")
    muscle_group: Optional[str] = Field(None, description="Группа мышц")
    sets: List[ExerciseSetCreate] = Field(..., description="Список подходов")
    raw_input_text: Optional[str] = Field(None, description="Оригинальный текст этого упражнения")


class WorkoutCreate(BaseModel):
    """
    Запрос на добавление всей тренировки.
    Принимает список упражнений от AI Service.
    """
    exercises: List[ExerciseCreate] = Field(..., description="Список упражнений в тренировке")


class WorkoutResponse(BaseModel):
    """
    Ответ после сохранения тренировки.
    """
    id: int
    workout_date: date


class SummaryResponse(BaseModel):
    """
    Ответ с агрегированной статистикой.
    """
    period_days: int
    total_calories: float
    avg_calories_per_day: float
    total_protein: float
    avg_protein_per_day: float
    total_fat: float
    avg_fat_per_day: float
    total_carbs: float
    avg_carbs_per_day: float
    total_workouts: int
    total_volume_kg: Optional[float] = None