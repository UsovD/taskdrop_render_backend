#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

DB = "db.sqlite3"

def migrate_user_tasks():
    # ID пользователя, который нужно обновить
    old_user_id = 1
    new_user_id = 25278733  # ID из Telegram
    
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        
        # Проверяем, существует ли пользователь с новым ID
        c.execute("SELECT * FROM users WHERE id = ?", (new_user_id,))
        user = c.fetchone()
        
        if not user:
            # Если пользователя с новым ID нет, создаем его
            print("Создаем пользователя с ID {}...".format(new_user_id))
            c.execute("""
                INSERT INTO users (id, telegram_id, first_name, last_name, username)
                VALUES (?, ?, ?, ?, ?)
            """, (new_user_id, new_user_id, "Telegram", "User", "telegramuser"))
        
        # Получаем все задачи пользователя со старым ID
        c.execute("SELECT id FROM tasks WHERE user_id = ?", (old_user_id,))
        task_ids = [row[0] for row in c.fetchall()]
        
        if task_ids:
            print("Найдено {} задач для пользователя с ID {}".format(len(task_ids), old_user_id))
            
            # Обновляем user_id задач
            c.execute("UPDATE tasks SET user_id = ? WHERE user_id = ?", (new_user_id, old_user_id))
            
            print("Задачи перенесены на пользователя с ID {}".format(new_user_id))
        else:
            print("Задачи для пользователя с ID {} не найдены".format(old_user_id))
        
        # Проверяем результат
        c.execute("SELECT id, user_id, title FROM tasks WHERE user_id = ?", (new_user_id,))
        migrated_tasks = c.fetchall()
        
        print("\nЗадачи после миграции:")
        for task in migrated_tasks:
            print(task)
        
        conn.commit()
        print("\nМиграция завершена успешно")

if __name__ == "__main__":
    migrate_user_tasks() 