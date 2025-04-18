# TaskDrop API Backend

Бэкенд для приложения управления задачами TaskDrop.

## Стек технологий

- Flask (Python)
- SQLite
- RESTful API

## Развертывание на Render.com

1. Создайте аккаунт на [Render.com](https://render.com/)
2. Создайте новый Web Service
3. Подключите репозиторий с кодом
4. Настройте следующие параметры:
   - **Name**: taskdrop-render-backend
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt && python init_db.py`
   - **Start Command**: `gunicorn app:app`
   - **Root Directory**: `backend`

## Локальная разработка

1. Клонируйте репозиторий
2. Перейдите в директорию бэкенда: `cd backend`
3. Создайте виртуальное окружение: `python -m venv venv`
4. Активируйте окружение:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. Установите зависимости: `pip install -r requirements.txt`
6. Инициализируйте базу данных: `python init_db.py`
7. Запустите приложение: `python app.py`

## API Endpoints

- `GET /tasks` - получить список задач
- `GET /tasks/:id` - получить конкретную задачу
- `POST /tasks` - создать новую задачу
- `PUT /tasks/:id` - обновить задачу
- `DELETE /tasks/:id` - удалить задачу

## Структура проекта

- `app.py` - основной файл приложения
- `init_db.py` - скрипт для инициализации базы данных
- `db.sqlite3` - файл базы данных
- `requirements.txt` - зависимости проекта
- `render.yaml` - конфигурация для Render.com 