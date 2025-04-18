#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

DB = "db.sqlite3"

def check_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        
        # Проверяем структуру таблицы users
        print("=== Структура таблицы users ===")
        c.execute("PRAGMA table_info(users)")
        for column in c.fetchall():
            print(column)
        
        # Выводим пользователей
        print("\n=== Пользователи ===")
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        for user in users:
            print(user)
        
        # Выводим задачи
        print("\n=== Задачи ===")
        c.execute("SELECT id, user_id, title FROM tasks")
        tasks = c.fetchall()
        for task in tasks:
            print(task)

if __name__ == "__main__":
    check_db() 