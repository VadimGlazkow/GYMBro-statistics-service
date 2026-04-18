from fastapi import APIRouter, Depends, Query
from app.schemas import SummaryResponse
from app.security import get_current_user

router = APIRouter(
    prefix="/summary",
    tags=["summary"]
)


@router.get("/")
async def get_summary(
    period: str = Query("30d", enum=["7d", "30d", "90d"]),
    user_id: int = Depends(get_current_user)
):
    """
    ЗАГЛУШКА: Получение статистики за период.
    """
    return SummaryResponse(
        period_days=30,
        total_calories=74400.0,
        avg_calories_per_day=2480.0,
        total_protein=4260.0,
        avg_protein_per_day=142.0,
        total_fat=2340.0,
        avg_fat_per_day=78.0,
        total_carbs=6300.0,
        avg_carbs_per_day=210.0,
        total_workouts=12,
        total_volume_kg=48200.0
    )