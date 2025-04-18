import sqlite3

DB = "db.sqlite3"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("База данных инициализирована успешно.")

if __name__ == "__main__":
    init_db() 