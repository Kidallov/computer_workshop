# Лабораторная работа: Получение размеров PNG-изображения

## Цель

Реализовать веб-приложение, которое:
- По маршруту `/login` возвращает логин в системе MOODLE;
- По маршруту `/size2json` принимает PNG-файл, возвращает его ширину и высоту в JSON;
- Отвечает ошибкой, если файл не PNG.

## Используемые технологии

- Язык: Python 3.9+
- Framework: FastAPI
- Библиотеки: Pillow, python-multipart, uvicorn

## Маршруты

### `/login`  
Метод: `GET`  
Возвращает:
json {"author": "1147335"}

## 📄 main.py — основной код приложения

```
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO

app = FastAPI()

MOODLE_LOGIN = "kid_alov_aa"

@app.post("/size2json")
async def get_image_size(image: UploadFile = File(...)):
    if not image.filename.lower().endswith(".png"):
        return JSONResponse(content={"result": "invalid filetype"}, media_type="application/json")

    try:
        contents = await image.read()
        img = Image.open(BytesIO(contents))
        width, height = img.size
        return JSONResponse(content={"width": width, "height": height}, media_type="application/json")
    except Exception:
        return JSONResponse(content={"result": "invalid filetype"}, media_type="application/json")

@app.get("/login")
def get_login():
    return JSONResponse(content={"author": MOODLE_LOGIN}, media_type="application/json")
```

## Вывод

Сервис успешно обрабатывает PNG-файлы и сообщает размеры изображения в пикселях. Все данные возвращаются в формате JSON с корректными заголовками.

