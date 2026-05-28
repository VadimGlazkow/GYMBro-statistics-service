from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date

from app.database import get_db
from app.models import Workout, ExerciseLog, FoodIntake
from app.schemas import (
    CombinedStatsResponse,
    WorkoutPeriodStats,
    NutritionPeriodStats,
    DailyWorkoutSummary,
    ExercisePeriodStats,
    DailyNutritionSummary,
)
from app.security import get_current_user

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/period", response_model=CombinedStatsResponse)
async def get_period_stats(
    start_date: date = Query(..., description="Начало периода (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Конец периода (YYYY-MM-DD)"),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CombinedStatsResponse:
    """
    Возвращает агрегированную статистику за период.
    Формат строго соответствует контракту AI Service для /recommendation/
    """
    period_days = (end_date - start_date).days + 1

    workouts = (
        db.query(Workout)
        .filter(
            Workout.user_id == user_id,
            Workout.workout_date >= start_date,
            Workout.workout_date <= end_date,
        )
        .options(joinedload(Workout.exercise_logs).joinedload(ExerciseLog.sets))
        .order_by(Workout.workout_date)
        .all()
    )

    exercise_stats_map: dict[str, dict] = defaultdict(
        lambda: {
            "muscle_group": None,
            "total_sets": 0,
            "workout_ids": set(),
            "weights": [],
            "durations": [],
            "distances": [],
        }
    )
    daily_workouts: dict[date, list[str]] = defaultdict(list)

    for workout in workouts:
        for log in workout.exercise_logs:
            stats = exercise_stats_map[log.exercise_name]
            if log.muscle_group:
                stats["muscle_group"] = log.muscle_group
            stats["workout_ids"].add(workout.id)
            daily_workouts[workout.workout_date].append(log.exercise_name)

            for set_row in log.sets:
                stats["total_sets"] += 1
                if set_row.weight_kg is not None:
                    stats["weights"].append(set_row.weight_kg)
                if set_row.duration_seconds is not None:
                    stats["durations"].append(set_row.duration_seconds)
                if set_row.distance_km is not None:
                    stats["distances"].append(set_row.distance_km)

    exercise_stats = [
        ExercisePeriodStats(
            exercise_name=name,
            muscle_group=data["muscle_group"],
            total_sets=data["total_sets"],
            avg_sets_per_workout=round(
                data["total_sets"] / len(data["workout_ids"]), 2
            )
            if data["workout_ids"]
            else 0.0,
            max_weight_kg=max(data["weights"]) if data["weights"] else None,
            avg_weight_kg=round(sum(data["weights"]) / len(data["weights"]), 2)
            if data["weights"]
            else None,
            max_duration_seconds=max(data["durations"]) if data["durations"] else None,
            avg_duration_seconds=round(
                sum(data["durations"]) / len(data["durations"]), 2
            )
            if data["durations"]
            else None,
            max_distance_km=max(data["distances"]) if data["distances"] else None,
            avg_distance_km=round(sum(data["distances"]) / len(data["distances"]), 2)
            if data["distances"]
            else None,
        )
        for name, data in sorted(exercise_stats_map.items())
    ]

    daily_workout_summaries = [
        DailyWorkoutSummary(
            date=workout_date,
            exercises=list(dict.fromkeys(exercises)),
        )
        for workout_date, exercises in sorted(daily_workouts.items())
    ]

    food_records = (
        db.query(FoodIntake)
        .filter(
            FoodIntake.user_id == user_id,
            FoodIntake.intake_date >= start_date,
            FoodIntake.intake_date <= end_date,
        )
        .order_by(FoodIntake.intake_date)
        .all()
    )

    daily_nutrition_map: dict[date, dict[str, float]] = defaultdict(
        lambda: {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0}
    )
    for record in food_records:
        daily = daily_nutrition_map[record.intake_date]
        daily["calories"] += record.calories or 0.0
        daily["protein"] += record.protein or 0.0
        daily["fat"] += record.fat or 0.0
        daily["carbs"] += record.carbs or 0.0

    daily_nutrition_summaries = [
        DailyNutritionSummary(
            date=intake_date,
            calories=round(totals["calories"], 2),
            protein=round(totals["protein"], 2),
            fat=round(totals["fat"], 2),
            carbs=round(totals["carbs"], 2),
        )
        for intake_date, totals in sorted(daily_nutrition_map.items())
    ]

    if daily_nutrition_summaries:
        days_count = len(daily_nutrition_summaries)
        avg_calories = round(
            sum(d.calories for d in daily_nutrition_summaries) / days_count, 2
        )
        avg_protein = round(
            sum(d.protein for d in daily_nutrition_summaries) / days_count, 2
        )
        avg_fat = round(sum(d.fat for d in daily_nutrition_summaries) / days_count, 2)
        avg_carbs = round(
            sum(d.carbs for d in daily_nutrition_summaries) / days_count, 2
        )
    else:
        avg_calories = avg_protein = avg_fat = avg_carbs = 0.0

    return CombinedStatsResponse(
        workouts=WorkoutPeriodStats(
            start_date=start_date,
            end_date=end_date,
            period_days=period_days,
            total_workouts=len(workouts),
            exercise_stats=exercise_stats,
            daily_summaries=daily_workout_summaries,
        ),
        nutrition=NutritionPeriodStats(
            start_date=start_date,
            end_date=end_date,
            period_days=period_days,
            avg_calories=avg_calories,
            avg_protein=avg_protein,
            avg_fat=avg_fat,
            avg_carbs=avg_carbs,
            daily_summaries=daily_nutrition_summaries,
        ),
    )
