import json
import time
import sqlite3

import db_functions
from parsers import parser_mephi, parser_mirea, parser_kfu

try:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
except FileNotFoundError:
    config = {
        "news_db": "news.db",
        "output_file": "newsletter.txt",
        "interval_minutes": 10
    }

NEWS_DB = config.get("news_db", "news.db")
OUTPUT_FILE = config.get("output_file", "newsletter.txt")
INTERVAL = config.get("interval_minutes", 10)


def prepare_databases():
    """Создание всех таблиц через db_functions."""
    connection, cursor = db_functions.connect(NEWS_DB)
    if connection and cursor:
        db_functions.create_news_table(cursor, connection)
        db_functions.create_categories_table(cursor, connection)
        db_functions.create_university_table(cursor, connection)
        db_functions.create_users_table(cursor, connection)
        db_functions.create_user_cat_table(cursor, connection)
        connection.close()


def run_parsers():
    parsers = [
        ("МИФИ", parser_mephi.parse),
        ("МИРЭА", parser_mirea.parse),
        ("КФУ", parser_kfu.parse),
    ]

    for name, parse_function in parsers:
        try:
            print(f"[INFO] Сбор новостей: {name}")
            parse_function()
        except Exception as error:
            print(f"[ERROR] Ошибка в парсере {name}: {error}")


def make_send_list(old_max_id):
    try:
        connection = sqlite3.connect(NEWS_DB)
        cursor = connection.cursor()

        # Новые новости, появившиеся после последнего круга
        news = cursor.execute(
            "SELECT id, category_id FROM news WHERE id > ? ORDER BY id;",
            (old_max_id,)
        ).fetchall()

        users = cursor.execute("SELECT id FROM users ORDER BY id;").fetchall()
        interests = cursor.execute("SELECT user_id, category_id FROM user_categories;").fetchall()
        connection.close()

        # Собираем подписки: {user_id: {cat_id1, cat_id2, ...}}
        user_categories = {}
        for user_id, category_id in interests:
            user_categories.setdefault(user_id, set()).add(category_id)

        # Записываем в файл рассылки
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            for (user_id,) in users:
                subscribed_cats = user_categories.get(user_id, set())
                matching_ids = [
                    str(news_id)
                    for news_id, cat_id in news
                    if cat_id in subscribed_cats
                ]
                if matching_ids:
                    file.write(f"{user_id}: {', '.join(matching_ids)}\n")

        print(f"[INFO] Новых новостей: {len(news)}")
        print(f"[INFO] Рассылка записана в {OUTPUT_FILE}")

    except sqlite3.Error as error:
        print(f"[ERROR] Ошибка при формировании рассылки: {error}")


def main():
    prepare_databases()

    while True:
        try:
            connection = sqlite3.connect(NEWS_DB)
            cursor = connection.cursor()
            row = cursor.execute("SELECT MAX(id) FROM news;").fetchone()
            old_max_id = row[0] if (row and row[0] is not None) else 0
            connection.close()

            run_parsers()

            make_send_list(old_max_id)
            print(f"[INFO] Круг завершён. Ожидание {INTERVAL} мин...\n")

            time.sleep(INTERVAL * 60)

        except KeyboardInterrupt:
            print("\nРабота завершена пользователем.")
            break
        except Exception as error:
            print(f"[ERROR] Непредвиденная ошибка: {error}")
            time.sleep(INTERVAL * 60)


if __name__ == "__main__":
    main()