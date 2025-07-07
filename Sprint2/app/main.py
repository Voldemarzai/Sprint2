"""
FastAPI приложение для работы с данными о перевалах.
Предоставляет API для добавления и получения информации.
"""

import logging
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models import *
from database import DatabaseManager
import uvicorn
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(
    title="Pereval API",
    description="API для работы с данными о горных перевалах",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация менеджера базы данных
db_manager = DatabaseManager()


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    logger.info("Starting Pereval API application")
    if not db_manager.connect():
        logger.error("Failed to connect to database on startup")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка ресурсов при завершении работы"""
    logger.info("Shutting down Pereval API application")
    db_manager.close()


@app.get("/submitData/{pereval_id}/",
         response_model=PerevalResponse,
         summary="Получить данные перевала по ID",
         tags=["Perevals"])
async def get_pereval(pereval_id: int):
    """Получает полную информацию о перевале по его ID"""
    try:
        pereval = db_manager.get_pereval_by_id(pereval_id)
        if not pereval:
            raise HTTPException(
                status_code=404,
                detail=f"Перевал с ID {pereval_id} не найден"
            )
        return pereval
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )

@app.patch("/submitData/{pereval_id}/",
           response_model=PerevalUpdateResponse,
           summary="Редактировать перевал",
           tags=["Perevals"])
async def update_pereval(pereval_id: int, request: PerevalSubmitRequest):
    """
    Редактирует существующий перевал.
    Доступно только для записей со статусом 'new'.
    Нельзя изменять данные пользователя (email, телефон, ФИО).
    """
    try:
        success = db_manager.update_pereval(
            pereval_id,
            request.data.dict(),
            [img.dict() for img in request.images],
            request.activities
        )
        return {
            "state": 1 if success else 0,
            "message": "Запись успешно обновлена" if success else "Не удалось обновить запись"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )

@app.get("/submitData/",
         response_model=UserPerevalsResponse,
         summary="Список перевалов пользователя",
         tags=["Perevals"])
async def get_user_perevals(user__email: str = Query(..., alias="user__email")):
    """Получает список всех перевалов, добавленных пользователем"""
    try:
        perevals = db_manager.get_perevals_by_email(user__email)
        return {"perevals": perevals}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )