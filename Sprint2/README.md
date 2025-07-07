# API для учёта горных перевалов

## Эндпоинты

### 1. Получить данные перевала
`GET /submitData/{id}/`

Пример ответа:
```json
{
  "id": 1,
  "status": "new",
  "beautyTitle": "пер.",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "user": {
    "email": "user@example.com",
    "phone": "+79001234567",
    "fam": "Иванов",
    "name": "Иван",
    "otc": "Иванович"
  },
  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525,
    "height": 1200
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {
      "title": "Седловина",
      "img_url": "https://example.com/image.jpg"
    }
  ],
  "activities": [1, 2]
}