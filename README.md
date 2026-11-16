# Домашнее задание к лекции «Создание REST API на FastAPI» (Часть 1)

## Описание проекта
Реализован сервис объявлений купли/продажи на фреймворке **FastAPI**. Проект упакован в Docker-контейнер.

## Реализованный функционал
- **POST `/advertisement`** — создание объявления.
- **GET `/advertisement/{advertisement_id}`** — получение объявления по ID.
- **PATCH `/advertisement/{advertisement_id}`** — частичное обновление объявления (обновляются только переданные поля).
- **DELETE `/advertisement/{advertisement_id}`** — удаление объявления.
- **GET `/advertisement?{query_string}`** — поиск и фильтрация по полям (title, author, min_price, max_price).

Поля объявления: заголовок, описание, цена, автор, дата создания. Авторизация не требуется.

## Стек технологий
- Python 3
- FastAPI
- Uvicorn
- Docker

## Как запустить проект локально (без Docker)
1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустите сервер:
   ```bash
   uvicorn main:app --reload
   ```

3. Документация доступна по адресу: `http://127.0.0.1:8000/docs`.

## Как запустить в Docker
1. Соберите образ:
   ```bash
   docker build -t fastapi-shop .
   ```

2. Запустите контейнер:
   ```bash
   docker run -p 8000:8000 fastapi-shop
   ```

3. Сервис будет доступен по адресу: `http://127.0.0.1:8000/docs`
