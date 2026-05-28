import httpx
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import FoodIntake
from app.schemas import NutritionCreateRequest, NutritionSaveResponse, NutritionResponse
from app.security import get_current_user

router = APIRouter(prefix="/food", tags=["food"])


@router.post("/", response_model=NutritionSaveResponse)
async def add_food(
    request: NutritionCreateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NutritionSaveResponse:
    """
    1. Принимает сырой текст от бота.
    2. Вызывает AI Service (/nutrition/calculate).
    3. Сохраняет результат в БД.
    """
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{settings.AI_SERVICE_URL.rstrip('/')}/nutrition/calculate",
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

    ai_data = NutritionResponse(**resp.json())

    if not ai_data.success:
        raise HTTPException(
            status_code=400,
            detail=ai_data.error_message or "AI Service вернул ошибку парсинга питания",
        )

    if not ai_data.items:
        raise HTTPException(status_code=400, detail="AI Service не вернул продукты")

    intake_date = request.intake_date or date.today()
    records: list[FoodIntake] = []

    for item in ai_data.items:
        record = FoodIntake(
            user_id=user_id,
            intake_date=intake_date,
            raw_text=request.raw_text,
            product_name=item.product_name,
            grams=item.grams,
            calories=item.calories,
            protein=item.protein,
            fat=item.fat,
            carbs=item.carbs,
        )
        db.add(record)
        records.append(record)

    db.commit()
    for record in records:
        db.refresh(record)

    return NutritionSaveResponse(
        success=True,
        intake_id=int(records[0].id),
        date=intake_date,
    )
