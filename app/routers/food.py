from fastapi import APIRouter, Depends
from app.schemas import FoodCreate, FoodResponse
from app.security import get_current_user

router = APIRouter(
    prefix="/food",
    tags=["food"]
)


@router.post("/", response_model=FoodResponse)
async def add_food(
    food: FoodCreate,
    user_id: int = Depends(get_current_user)
):
    """
    ЗАГЛУШКА: Добавление записи о питании.
    Принимает весь текст питания от пользователя.
    """
    # Здесь будет логика:
    # 1. Разбить raw_text по запятой
    # 2. Попытаться обработать через Nutrition API
    # 3. При неудаче отправить в AI Service

    return FoodResponse(
        success=True,
        items=[
            {
                "product_name": "Заглушка продукта",
                "grams": 100.0,
                "calories": 250.0,
                "protein": 20.0,
                "fat": 10.0,
                "carbs": 15.0
            }
        ],
        error_message=None,
        fallback_used=False
    )