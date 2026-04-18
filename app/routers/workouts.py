from fastapi import APIRouter, Depends
from app.schemas import WorkoutCreate, WorkoutResponse
from app.security import get_current_user

router = APIRouter(
    prefix="/workouts",
    tags=["workouts"]
)

@router.post("/", response_model=WorkoutResponse)
async def add_workout(
    workout: WorkoutCreate,
    user_id: int = Depends(get_current_user)
):
    """
    ЗАГЛУШКА: Добавление тренировки.
    Принимает уже распарсенный JSON от AI Service (Дмитрий).
    """
    # Здесь будет сохранение в БД:
    # - Создание записи в workouts
    # - Создание записей в exercise_logs
    # - Создание записей в exercise_sets

    return WorkoutResponse(
        id=999,
        workout_date="2026-04-17"
    )