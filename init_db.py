import sqlite3

DB = "db.sqlite3"

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        # Создаем таблицу users для хранения пользователей
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT,
                username TEXT,
                photo_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

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
        c.execute("SELECT * FROM users WHERE telegram_id = ?", (279058397,))
        if not c.fetchone():
            c.execute('''
                INSERT INTO users (telegram_id, first_name, last_name, username)
                VALUES (?, ?, ?, ?)
            ''', (279058397, 'Denis', 'Usov', 'denisusov'))
        
        conn.commit()
        print("База данных инициализирована успешно.")

if __name__ == "__main__":
    init_db() 