import sqlite3 as sql

def connect(db="news.db"):
    connection = None
    cursor = None
    try:
        connection = sql.connect(db)
        cursor = connection.cursor()
        return connection, cursor
    except sql.Error as e:
        print(f"[connect] Ошибка подключения к БД: {e}")
        if connection:
            connection.close()
        return None, None


def create_news_table(cursor, connection):
    try:
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS news(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    link TEXT UNIQUE NOT NULL,          
                    published_date TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    university_id INTEGER NOT NULL,
                    content TEXT,
                    added_at TEXT DEFAULT (datetime('now'))
                );
        """)
        connection.commit()
    except sql.Error as e:
        print(f"[create_news_table] Ошибка: {e}")
        connection.rollback()


def create_categories_table(cursor, connection):
    try:
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS news_categories(
                    category_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );
        """)

        num_cat = cursor.execute("SELECT COUNT(*) FROM news_categories;").fetchone()
        if num_cat[0] == 0:
            cursor.execute("""
                    INSERT INTO news_categories (category_id, name) VALUES
                        (1, "Наука и инновации"),
                        (2, 'Образование'),
                        (3, 'Студенческая жизнь'),
                        (4, 'Спорт'),
                        (5, 'Культура и творчество'),
                        (6, 'Международная деятельность'),
                        (7, 'Сотрудничество и партнёрство'),
                        (8, 'Объявления и события'),
                        (9, 'Абитуриентам'),
                        (10, 'Без категории');
            """)
        connection.commit()
    except sql.Error as e:
        print(f"[create_categories_table] Ошибка: {e}")
        connection.rollback()


def create_university_table(cursor, connection):
    try:
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS universities (
                    university_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );
        """)
        num_uni = cursor.execute("SELECT COUNT(*) FROM universities;").fetchone()
        if num_uni[0] == 0:
            cursor.execute("""
                    INSERT INTO universities (university_id, name) VALUES
                        (1, 'РЭУ'),
                        (2, 'МГУ'),
                        (3, 'МИФИ'),
                        (4, 'ВШЭ'),
                        (5, 'МИРЭА'),
                        (6, 'КФУ');
            """)
        connection.commit()
    except sql.Error as e:
        print(f"[create_university_tables] Ошибка: {e}")
        connection.rollback()


def get_university_id(cursor, name):
    try:
        university_id = cursor.execute(
                "SELECT university_id FROM universities WHERE name = ?;",
                (name,)
        ).fetchone()

        if university_id is not None:
            return university_id[0]
        return None

    except sql.Error as e:
        print(f"[get_university_id] Ошибка: {e}")
        return None


def get_category_id(cursor, cat):
    try:
        category_id = cursor.execute(
                "SELECT category_id FROM news_categories WHERE name = ?;",
                (cat,)
        ).fetchone()

        if category_id is not None:
            return category_id[0]
        return None

    except sql.Error as e:
        print(f"[get_category_id] Ошибка: {e}")
        return None


def get_last_link(cursor, university_id):
    try:
        row = cursor.execute("""
                SELECT link FROM news 
                WHERE university_id = ? 
                ORDER BY published_date DESC 
                LIMIT 1;""",
                (university_id,)).fetchone()

        if row is not None:
            return row[0]
        return None

    except sql.Error as e:
        print(f"[get_last_link] Ошибка: {e}")
        return None


def print_all_rows(cursor):
    try:
        cursor.execute('''
                SELECT * FROM news
        ''')
        print(cursor.fetchall())
    except sql.Error as e:
        print(f"[print_all_rows] Ошибка: {e}")


def insert_news(cursor, connection, title, link, published_date, category_id, university_id, content=""):
    try:
        cursor.execute("""
                INSERT OR IGNORE INTO news 
                (title, link, published_date, category_id, university_id, content)
                VALUES (?, ?, ?, ?, ?, ?);""",
                (title, link, published_date, category_id, university_id, content))
        connection.commit()
    except sql.Error as e:
        print(f"[insert_news] Ошибка: {e}")
        connection.rollback()


def create_users_table(cursor, connection):
    try:
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT
                );
        """)
        connection.commit()
    except sql.Error as e:
        print(f"[create_users_table] Ошибка: {e}")
        connection.rollback()


def create_user_cat_table(cursor, connection):
    try:
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_categories (
                    user_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
        """)
        connection.commit()
    except sql.Error as e:
        print(f"[create_user_cat_table] Ошибка: {e}")
        connection.rollback()









