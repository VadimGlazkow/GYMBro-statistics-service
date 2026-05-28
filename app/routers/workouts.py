import httpx
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Workout, ExerciseLog, ExerciseSet
from app.schemas import WorkoutCreateRequest, WorkoutSaveResponse, TrainingParseResponse
from app.security import get_current_user

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutSaveResponse)
async def add_workout(
    request: WorkoutCreateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkoutSaveResponse:
    """
    1. Принимает сырой текст тренировки.
    2. Вызывает AI Service (/training/parse).
    3. Сохраняет упражнения и подходы в БД.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.AI_SERVICE_URL.rstrip('/')}/training/parse",
                json={"raw_text": request.raw_text},
                headers={"Content-Type": "application/json"},
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI Service недоступен ({settings.AI_SERVICE_URL}): {e}",
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="AI Service вернул ошибку")

    ai_data = TrainingParseResponse(**resp.json())

    if not ai_data.success:
        raise HTTPException(
            status_code=400,
            detail=ai_data.error_message or "AI Service вернул ошибку парсинга тренировки",
        )

    if not ai_data.exercises:
        raise HTTPException(status_code=400, detail="AI Service не вернул упражнения")

    workout_date = request.workout_date or date.today()

    workout = Workout(
        user_id=user_id,
        workout_date=workout_date,
        raw_input_text=request.raw_text,
    )
    db.add(workout)
    db.flush()

    for exercise in ai_data.exercises:
        exercise_log = ExerciseLog(
            workout_id=workout.id,
            user_id=user_id,
            exercise_name=exercise.exercise_name,
            exercise_type=exercise.exercise_type,
            muscle_group=exercise.muscle_group,
            raw_input_text=exercise.raw_input_text,
        )
        db.add(exercise_log)
        db.flush()

        for set_data in exercise.sets:
            db.add(
                ExerciseSet(
                    exercise_log_id=exercise_log.id,
                    weight_kg=set_data.weight_kg,
                    reps=set_data.reps,
                    duration_seconds=set_data.duration_seconds,
                    distance_km=set_data.distance_km,
                    feeling=set_data.feeling,
                )
            )

    db.commit()
    db.refresh(workout)

    return WorkoutSaveResponse(
        success=True,
        workout_id=int(workout.id),
        date=workout_date,
    )
