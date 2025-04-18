from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
# Обновляем настройки CORS для разрешения всех источников запросов
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*"}})

DB = "db.sqlite3"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        # Изменяем структуру таблицы tasks, добавляя новые поля
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                due_time TEXT,
                notification TEXT,
                priority TEXT DEFAULT 'medium',
                tags TEXT,             /* JSON строка для хранения массива тегов */
                attachments TEXT,      /* JSON строка для хранения URL вложений */
                notes TEXT,
                location TEXT,
                repeat TEXT,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def dict_factory(cursor, row):
    """Преобразует строки SQLite в словари"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Добавляем API для работы с пользователями
@app.route("/users", methods=["GET"])
def get_users():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = c.fetchall()
        return jsonify(users)

@app.route("/users/telegram/<int:telegram_id>", methods=["GET"])
def get_user_by_telegram_id(telegram_id):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        # Теперь id и telegram_id одинаковые, но мы можем проверить по обоим полям для обратной совместимости
        c.execute("SELECT * FROM users WHERE id = ? OR telegram_id = ?", (telegram_id, telegram_id))
        user = c.fetchone()
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404

@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    telegram_id = data.get("telegram_id")
    first_name = data.get("first_name")
    
    if not telegram_id or not first_name:
        return jsonify({"error": "telegram_id and first_name are required"}), 400
    
    last_name = data.get("last_name")
    username = data.get("username")
    photo_url = data.get("photo_url")
    
    # Обрабатываем custom_id, если он есть
    custom_id = data.get("id")
    user_id = custom_id if custom_id is not None else telegram_id
    
    with sqlite3.connect(DB) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        
        # Проверяем, существует ли пользователь с таким ID или telegram_id
        c.execute("SELECT * FROM users WHERE id = ? OR telegram_id = ?", (user_id, telegram_id))
        existing_user = c.fetchone()
        
        if existing_user:
            # Обновляем существующего пользователя
            c.execute("""
                UPDATE users 
                SET first_name = ?, last_name = ?, username = ?, photo_url = ?, telegram_id = ?
                WHERE id = ?
            """, (first_name, last_name, username, photo_url, telegram_id, existing_user["id"]))
            conn.commit()
            
            c.execute("SELECT * FROM users WHERE id = ?", (existing_user["id"],))
            updated_user = c.fetchone()
            return jsonify(updated_user)
        else:
            # Создаем нового пользователя
            c.execute("""
                INSERT INTO users (id, telegram_id, first_name, last_name, username, photo_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, telegram_id, first_name, last_name, username, photo_url))
            conn.commit()
            
            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            new_user = c.fetchone()
            return jsonify(new_user), 201

@app.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = request.args.get("user_id")
    with sqlite3.connect(DB) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("""
            SELECT id, user_id, title, description, due_date, due_time, 
                   notification, priority, tags, attachments, notes, 
                   location, repeat, done, created_at 
            FROM tasks 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
        
        tasks = c.fetchall()
        
        # Преобразуем JSON-строки в объекты Python
        for task in tasks:
            task['done'] = bool(task['done'])
            if task['tags']:
                task['tags'] = json.loads(task['tags'])
            if task['attachments']:
                task['attachments'] = json.loads(task['attachments'])
        
        return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    user_id = data.get("user_id")
    
    # Извлекаем значения полей или устанавливаем None, если поле отсутствует
    title = data.get("title", "")
    description = data.get("description", "")
    due_date = data.get("due_date")
    due_time = data.get("due_time")
    notification = data.get("notification")
    priority = data.get("priority", "medium")
    tags = json.dumps(data.get("tags", [])) if data.get("tags") else None
    attachments = json.dumps(data.get("attachments", [])) if data.get("attachments") else None
    notes = data.get("notes")
    location = data.get("location")
    repeat = data.get("repeat")
    
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO tasks (
                user_id, title, description, due_date, due_time, 
                notification, priority, tags, attachments, notes, 
                location, repeat
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, title, description, due_date, due_time, 
            notification, priority, tags, attachments, notes, 
            location, repeat
        ))
        conn.commit()
        task_id = c.lastrowid
        
        # Получаем созданную задачу
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("""
            SELECT id, user_id, title, description, due_date, due_time, 
                   notification, priority, tags, attachments, notes, 
                   location, repeat, done, created_at 
            FROM tasks 
            WHERE id = ?
        """, (task_id,))
        task = c.fetchone()
        task['done'] = bool(task['done'])
        if task['tags']:
            task['tags'] = json.loads(task['tags'])
        if task['attachments']:
            task['attachments'] = json.loads(task['attachments'])
    
    return jsonify(task)

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return jsonify({"success": True})

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    
    # Проверяем наличие полей в запросе и формируем SQL запрос
    fields = []
    values = []
    
    field_mappings = {
        "title": "title",
        "description": "description",
        "due_date": "due_date",
        "due_time": "due_time",
        "notification": "notification",
        "priority": "priority",
        "done": "done",
        "notes": "notes",
        "location": "location",
        "repeat": "repeat"
    }
    
    for client_field, db_field in field_mappings.items():
        if client_field in data:
            value = data[client_field]
            if client_field == "done":
                value = int(value)
            fields.append(f"{db_field} = ?")
            values.append(value)
    
    # Обработка JSON полей
    if "tags" in data:
        fields.append("tags = ?")
        values.append(json.dumps(data["tags"]) if data["tags"] else None)
    
    if "attachments" in data:
        fields.append("attachments = ?")
        values.append(json.dumps(data["attachments"]) if data["attachments"] else None)
    
    if not fields:
        return jsonify({"success": False, "error": "No fields to update"}), 400
    
    values.append(task_id)  # Добавляем id задачи в конец списка значений
    
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        
        # Возвращаем обновленную задачу
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("""
            SELECT id, user_id, title, description, due_date, due_time, 
                   notification, priority, tags, attachments, notes, 
                   location, repeat, done, created_at 
            FROM tasks 
            WHERE id = ?
        """, (task_id,))
        task = c.fetchone()
        
        if task:
            task['done'] = bool(task['done'])
            if task['tags']:
                task['tags'] = json.loads(task['tags'])
            if task['attachments']:
                task['attachments'] = json.loads(task['attachments'])
    
    return jsonify(task)

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("""
            SELECT id, user_id, title, description, due_date, due_time, 
                   notification, priority, tags, attachments, notes, 
                   location, repeat, done, created_at 
            FROM tasks 
            WHERE id = ?
        """, (task_id,))
        
        task = c.fetchone()
        
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        # Преобразуем JSON-строки в объекты Python
        task['done'] = bool(task['done'])
        if task['tags']:
            task['tags'] = json.loads(task['tags'])
        if task['attachments']:
            task['attachments'] = json.loads(task['attachments'])
        
        return jsonify(task)

if __name__ == "__main__":
    init_db()
    # Используем переменные окружения для хоста и порта, чтобы приложение работало на Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False) 