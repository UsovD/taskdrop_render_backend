from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB = "db.sqlite3"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@app.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = request.args.get("user_id")
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = c.fetchall()
        tasks = [{
            "id": row[0],
            "user_id": row[1],
            "text": row[2],
            "done": bool(row[3]),
            "created_at": row[4]
        } for row in rows]
        return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    user_id = data.get("user_id")
    text = data.get("text")
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (user_id, text) VALUES (?, ?)", (user_id, text))
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
    done = data.get("done")
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("UPDATE tasks SET done = ? WHERE id = ?", (int(done), task_id))
        conn.commit()
    return jsonify({"success": True})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)