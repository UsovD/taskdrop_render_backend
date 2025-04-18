from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

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
    
    return jsonify({"success": True, "id": task_id})

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
    app.run(debug=True)
