#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import codecs

DB = "db.sqlite3"

def check_user_tasks(user_id):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        
        # Получаем информацию о пользователе
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        
        if user:
            print("\n=== Пользователь ===")
            print("ID: {}".format(user[0]).encode('utf-8'))
            print("Telegram ID: {}".format(user[1]).encode('utf-8'))
            print("Имя: {} {}".format(user[2], user[3] or "").encode('utf-8'))
            print("Ник: {}".format(user[4] or "").encode('utf-8'))
        else:
            print("Пользователь с ID {} не найден".format(user_id).encode('utf-8'))
            return
        
        # Выводим задачи пользователя
        print("\n=== Задачи пользователя ===")
        c.execute("""
            SELECT id, title, description, due_date, due_time, notification, priority, done
            FROM tasks
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        tasks = c.fetchall()
        
        if tasks:
            for i, task in enumerate(tasks):
                task_id, title, description, due_date, due_time, notification, priority, done = task
                print("\nЗадача #{} - {}".format(task_id, title.encode('utf-8') if title else ""))
                if description:
                    print("Описание: {}".format(description.encode('utf-8')))
                print("Срок: {} {}".format(due_date or "-", due_time or "").encode('utf-8'))
                if notification:
                    print("Уведомление: {}".format(notification.encode('utf-8')))
                print("Приоритет: {}".format(priority.encode('utf-8')))
                status = "Выполнено" if done else "Активна"
                print("Статус: {}".format(status.encode('utf-8')))
        else:
            print("Задачи не найдены".encode('utf-8'))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])
    else:
        user_id = 25278733  # По умолчанию проверяем пользователя с Telegram ID
    
    check_user_tasks(user_id) 