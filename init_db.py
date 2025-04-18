#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

DB = "db.sqlite3"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        
        # Создаем временную таблицу для миграции данных пользователей
        c.execute('''
            CREATE TABLE IF NOT EXISTS users_new (
                id INTEGER PRIMARY KEY,  /* id теперь будет равен telegram_id */
                telegram_id INTEGER,
                first_name TEXT NOT NULL,
                last_name TEXT,
                username TEXT,
                photo_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Проверяем, существует ли таблица users
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if c.fetchone():
            # Копируем данные из старой таблицы в новую, используя telegram_id как id
            c.execute('''
                INSERT OR IGNORE INTO users_new (id, telegram_id, first_name, last_name, username, photo_url, created_at)
                SELECT telegram_id, telegram_id, first_name, last_name, username, photo_url, created_at
                FROM users
            ''')
            
            # Получаем задачи и обновляем user_id на telegram_id
            c.execute("SELECT id, user_id FROM tasks")
            tasks = c.fetchall()
            
            # Получаем соответствие user_id и telegram_id
            c.execute("SELECT id, telegram_id FROM users")
            user_mappings = {uid: tid for uid, tid in c.fetchall() if tid is not None}
            
            # Удаляем старую таблицу users
            c.execute("DROP TABLE users")
            
            # Переименовываем новую таблицу
            c.execute("ALTER TABLE users_new RENAME TO users")
            
            # Обновляем связи задач с пользователями
            for task_id, user_id in tasks:
                if user_id in user_mappings:
                    c.execute("UPDATE tasks SET user_id = ? WHERE id = ?", (user_mappings[user_id], task_id))
        else:
            # Если таблицы users еще нет, просто переименовываем временную таблицу
            c.execute("ALTER TABLE users_new RENAME TO users")

        # Создаем таблицу tasks
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Добавляем тестового пользователя, если он еще не существует
        c.execute("SELECT * FROM users WHERE id = ?", (279058397,))
        if not c.fetchone():
            c.execute('''
                INSERT INTO users (id, telegram_id, first_name, last_name, username)
                VALUES (?, ?, ?, ?, ?)
            ''', (279058397, 279058397, 'Denis', 'Usov', 'denisusov'))
        
        conn.commit()
        print("База данных инициализирована успешно.")

if __name__ == "__main__":
    init_db() 