from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.food import router as food_router
from app.routers.workouts import router as workouts_router
from app.routers.summary import router as summary_router


app = FastAPI(
    title="Statistics Service",
    description="Сервис хранения тренировок и питания + агрегация статистики",
    version="0.1.0",
    docs_url="/docs",      # Swagger документация
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(food_router)
app.include_router(workouts_router)
app.include_router(summary_router)


@app.get("/")
async def root():
    """
    Простая проверочная ручка.
    Показывает, что Statistics Service работает.
    """
    return {
        "message": "Statistics Service is running",
        "status": "ok",
        "version": "0.1.0",
        "documentation": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Ловит все необработанные ошибки и возвращает понятный JSON.
    """
    return {
        "success": False,
        "error_message": "Произошла внутренняя ошибка сервера",
        "detail": str(exc)
    }