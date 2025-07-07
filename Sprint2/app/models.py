from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    """
    Модель пользователя, который добавляет информацию о перевале.
    """
    email: str = Field(..., example="user@example.com", description="Email пользователя")
    phone: str = Field(..., example="+79001234567", description="Телефон пользователя")
    fam: str = Field(..., example="Иванов", description="Фамилия пользователя")
    name: str = Field(..., example="Иван", description="Имя пользователя")
    otc: Optional[str] = Field(None, example="Иванович", description="Отчество пользователя")

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email должен содержать @')
        return v

class Coords(BaseModel):
    """
    Модель географических координат перевала.
    """
    latitude: float = Field(..., example=45.3842, description="Широта")
    longitude: float = Field(..., example=7.1525, description="Долгота")
    height: int = Field(..., example=1200, description="Высота")

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Широта должна быть между -90 и 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Долгота должна быть между -180 и 180')
        return v

class Level(BaseModel):
    """
    Модель уровня сложности перевала в разные сезоны.
    """
    winter: Optional[str] = Field("", example="1A", description="Зимний уровень сложности")
    summer: Optional[str] = Field("", example="1B", description="Летний уровень сложности")
    autumn: Optional[str] = Field("", example="2A", description="Осенний уровень сложности")
    spring: Optional[str] = Field("", example="2B", description="Весенний уровень сложности")

class Image(BaseModel):
    """
    Модель изображения перевала.
    """
    title: str = Field(..., example="Седловина", description="Название изображения")
    img_url: str = Field(..., example="https://example.com/image.jpg", description="URL изображения")

class PerevalData(BaseModel):
    beautyTitle: str = Field(..., example="пер.", description="Краткое название перевала")
    title: str = Field(..., example="Пхия", description="Название перевала")
    other_titles: str = Field(..., example="Триев", description="Альтернативные названия")
    connect: str = Field(..., example="", description="Соединения с другими перевалами")  # Оставляем как есть
    user: User
    coords: Coords
    level: Level

class PerevalSubmitRequest(BaseModel):
    """
    Модель запроса на добавление нового перевала.
    """
    data: PerevalData
    images: List[Image]
    activities: List[int] = Field(..., example=[1, 2], description="ID видов деятельности")

class SubmitResponse(BaseModel):
    """
    Модель ответа после добавления перевала.
    """
    status: int = Field(..., example=200, description="HTTP статус код")
    message: str = Field(..., example="Запись успешно добавлена", description="Сообщение о результате")
    id: Optional[int] = Field(None, example=1, description="ID добавленного перевала")

class Activity(BaseModel):
    """
    Модель вида деятельности для перевала.
    """
    id: int = Field(..., example=1, description="ID вида деятельности")
    title: str = Field(..., example="пешком", description="Название вида деятельности")

class ActivitiesResponse(BaseModel):
    """
    Модель ответа со списком видов деятельности.
    """
    activities: List[Activity]
class PerevalResponse(BaseModel):
    id: int
    status: str
    beautyTitle: str
    title: str
    other_titles: str
    connect: str
    user: User
    coords: Coords
    level: Level
    images: List[Image]
    activities: List[int]

class PerevalUpdateResponse(BaseModel):
    state: int = Field(..., description="1 - успешно, 0 - ошибка")
    message: str = Field(..., description="Описание результата")

class PerevalShortInfo(BaseModel):
    id: int
    title: str
    status: str
    date_added: Optional[str]

class UserPerevalsResponse(BaseModel):
    perevals: List[PerevalShortInfo]