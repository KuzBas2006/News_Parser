import json
import sqlite3
import os

CONFIG_FILE = "config.json"
db_name = "news.db"

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            config = json.load(file)
            db_name = config.get("users_db", config.get("news_db", "news.db"))
    except Exception as e:
        print(f"[WARNING] {e}")

print(f"[INFO] Подключение к базе данных: {db_name}")

connection = sqlite3.connect(db_name)
cursor = connection.cursor()

# Создаем таблицы пользователей, если их нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_categories (
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, category_id)
);
""")

# Определяем точное имя колонки категорий в существующей таблице (id или category_id)
cursor.execute("PRAGMA table_info(news_categories);")
cols = [col[1] for col in cursor.fetchall()]
cat_col = "category_id" if "category_id" in cols else "id"

categories = [
    (1, "Наука и инновации"),
    (2, "Образование"),
    (3, "Студенческая жизнь"),
    (4, "Спорт"),
    (5, "Международное сотрудничество"),
    (6, "Культура и творчество")
]

# Вставляем с реальным именем колонки
cursor.executemany(f"""
INSERT OR IGNORE INTO news_categories ({cat_col}, name)
VALUES (?, ?);
""", categories)

test_users = [
    (1, "Алексей Смирнов", "smirnov_alex@yandex.ru"),
    (2, "Дарья Кузнецова", "daria.kuz@gmail.com"),
    (3, "Максим Васильев", "m.vasiliev@edu.ru"),
    (4, "Елена Морозова", "morozova_elena@inbox.ru"),
    (5, "Кирилл Романов", "romanov_k@vk.com"),
    (6, "София Новикова", "novikova.sofia@mail.ru")
]

cursor.executemany("""
INSERT OR IGNORE INTO users (id, name, email)
VALUES (?, ?, ?);
""", test_users)

test_user_categories = [
    (1, 1),
    (1, 4),
    (2, 2),
    (2, 3),
    (3, 1),
    (3, 5),
    (4, 3),
    (4, 6),
    (5, 1),
    (5, 4),
    (6, 2),
    (6, 6)
]

cursor.executemany("""
INSERT OR IGNORE INTO user_categories (user_id, category_id)
VALUES (?, ?);
""", test_user_categories)

connection.commit()

users_count = cursor.execute("SELECT COUNT(*) FROM users;").fetchone()[0]
user_cat_count = cursor.execute("SELECT COUNT(*) FROM user_categories;").fetchone()[0]

print(f"[SUCCESS] База данных заполнена: {users_count} пользователей, {user_cat_count} подписок.")

connection.close()