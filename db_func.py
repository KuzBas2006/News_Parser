import sqlite3


def connect_get_cursor(db):
    conn = None
    cursor = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"[connect_get_cursor] Ошибка подключения к БД: {e}")
        if conn:
            conn.close()
        return None, None


def create_news_table(cursor, conn):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news( 
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                published_date TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                university_id INTEGER NOT NULL,
                content TEXT,
                added_at TEXT DEFAULT (datetime('now'))
            ); 
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"[create_news_table] Ошибка: {e}")
        conn.rollback()


def create_categories_table(cursor, conn):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_categories (
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL
            );
        ''')

        num = cursor.execute('''
            SELECT COUNT(*) FROM news_categories;
        ''').fetchone()

        if num[0] == 0:
            cursor.execute('''
                INSERT INTO news_categories (category_id, name) VALUES
                (1, 'Наука и инновации'),
                (2, 'Образование'),
                (3, 'Студенческая жизнь'),
                (4, 'Спорт'),
                (5, 'Культура и творчество'),
                (6, 'Международная деятельность'),
                (7, 'Сотрудничество и партнёрство'),
                (8, 'Объявления и события'),
                (9, 'Абитуриентам'),
                (10, 'Без категории')
            ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"[create_categories_table] Ошибка: {e}")
        conn.rollback()


def create_university_tables(cursor, conn):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS universities (
                university_id INTEGER NOT NULL,
                name TEXT NOT NULL
            );
        ''')

        num = cursor.execute('''
            SELECT COUNT(*) FROM universities;
        ''').fetchone()
        if num[0] == 0:
            cursor.execute('''
                INSERT INTO universities (university_id, name) VALUES 
                (1, 'МАИ'),
                (2, 'РЭУ'),
                (3, 'МИФИ'),
                (4, 'ВШЭ'),
                (5, 'МИРЭА'),
                (6, 'КФУ')
            ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"[create_university_tables] Ошибка: {e}")
        conn.rollback()


def get_university_id(cursor, name):
    try:
        uni_id = cursor.execute('''
            SELECT university_id FROM universities
            WHERE name = ?;
        ''', (name,)).fetchone()
        return uni_id[0] if uni_id else None
    except sqlite3.Error as e:
        print(f"[get_university_id] Ошибка: {e}")
        return None
    finally:
        pass


def get_category_id(cursor, cat):
    try:
        cat_id = cursor.execute('''
            SELECT category_id FROM news_categories
            WHERE name = ?;
        ''', (cat,)).fetchone()
        return cat_id[0] if cat_id else None
    except sqlite3.Error as e:
        print(f"[get_category_id] Ошибка: {e}")
        return None


def get_last_link(cursor):
    try:
        row = cursor.execute('''
            SELECT link FROM news n
            JOIN universities u ON u.university_id = n.university_id
            WHERE u.name = 'МИРЭА'
            ORDER BY published_date DESC
            LIMIT 1;
        ''').fetchone()

        link = row[0] if row else None
        return link
    except sqlite3.Error as e:
        print(f"[get_last_link] Ошибка: {e}")
        return None


def print_all_rows(cursor):
    try:
        cursor.execute('''
            SELECT * 
            FROM news
        ''')
        print(cursor.fetchall())
    except sqlite3.Error as e:
        print(f"[print_all_rows] Ошибка: {e}")


def insert_news(cursor, conn, title, link, dt, category_id, university_id, content):
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO news (title, link, published_date, category_id, university_id, content) VALUES (?, ?, ?, ?, ?, ?);
        ''', (title, link, dt, category_id, university_id, content))
        conn.commit()
    except sqlite3.Error as e:
        print(f"[insert_news] Ошибка: {e}")
        conn.rollback()


def create_users_table(cursor, conn):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT
            );
        ''')

        num = cursor.execute('''
                SELECT COUNT(*) FROM users;
            ''').fetchone()

        if num[0] == 0:
            cursor.execute('''
                INSERT INTO users (id, name) VALUES
                (1, 'John'),
                (2, 'Mark'),
                (3, 'Ivanka'),
                (4, 'Maynard'),
                (5, 'Mathew')
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"[create_users_table] Ошибка: {e}")
        conn.rollback()


def create_user_cat_table(cursor, conn):
    try:
        cursor.execute('''
               CREATE TABLE IF NOT EXISTS user_categories (
                   user_id INTEGER NOT NULL,
                   category_id INTEGER NOT NULL,
                   FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
               );
           ''')

        num = cursor.execute('''
                   SELECT COUNT(*) FROM user_categories;
               ''').fetchone()

        if num[0] == 0:
            cursor.execute('''
                   INSERT INTO user_categories (user_id, category_id) VALUES
                   (1, 1),
                   (1, 2),
                   (2, 3),
                   (2, 4),
                   (3, 5),
                   (3, 6),
                   (4, 7),
                   (4, 8),
                   (5, 9),
                   (5, 1)
               ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"[create_user_cat_table] Ошибка: {e}")
        conn.rollback()