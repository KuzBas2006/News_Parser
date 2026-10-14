from bs4 import BeautifulSoup
import requests
from datetime import datetime


from db_functions import (
    connect,
    create_news_table,
    create_categories_table,
    create_university_table,
    create_users_table,
    create_user_cat_table,
    get_university_id,
    get_category_id,
    get_last_link,
    insert_news,
    print_all_rows
)

categories = {
    "Наука и инновации":                ["наук", "исследован", "лаборатор", "моделирован", "разработк"],
    "Образование":                      ["лекци", "тренинг", "олимпиад", "учебн"],
    "Студенческая жизнь":               ["стипенди", "конкурс", "кампус", "общежити", "студент"],
    "Спорт":                            ["спорт", "матч", "турнир", "соревнован", "чемпионат"],
    "Культура и творчество":            ["фестиваль", "концерт", "выставк", "творчеств"],
    "Международная деятельность":       ["международн", "иностран", "зарубеж"],
    "Сотрудничество и партнёрство":     ["партнер", "росатом", "соглашени", "сотрудничеств"],
    "Объявления и события":             ["анонс", "приглаша", "открыт набор", "внимание"],
    "Абитуриентам":                     ["абитуриент", "поступлени", "приемн", "дод", "день открытых дверей"],
    "Без категории":                    []
}

def guess_category_by_title(title):
    title_lower = title.lower()                           # все буквы маленькие
    for category_name, keywords in categories.items():    # послед-но берутся пары из словаря
        for keyword in keywords:
            if keyword in title_lower:
                return category_name
    return "Без категории"


def fetch_page(url, headers, cursor, connection, last_link, university_id):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Ошибка загрузки страницы: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Ошибка сети: {e}")
        return False

    soup = BeautifulSoup(response.text, features="html.parser")
    cards = soup.select(".views-row")  # Карточки новостей МИФИ

    if not cards:
        print("Новостей больше нет")
        return False
    for card in cards:
        # 1. Заголовок и ссылка
        link_tag = card.select_one("a")
        if not link_tag:
            continue
        title = link_tag.text.strip()
        link = link_tag.get("href", "")
        if not link or not title:
            continue

        if link.startswith("/"):
            link = "https://mephi.ru" + link
        elif not link.startswith("http"):
            link = "https://mephi.ru/" + link

        # Если дошли до последней сохраненной ссылки, то останавливаемся
        if last_link and link == last_link:
            print("Достигли ранее сохраненной новости, завершаем сбор.")
            return False
        # Дата
        time_tag = card.select_one("time")
        if time_tag:
            date = time_tag.get("datetime") or time_tag.text.strip()
        else:
            date = datetime.now().strftime("%Y-%m-%d")

        # Категория по заголовку
        cat_name = guess_category_by_title(title)
        category_id = get_category_id(cursor, cat_name)
        if category_id is None:
            category_id = get_category_id(cursor, "Без категории")

        insert_news(cursor, connection, title, link, date, category_id, university_id)

    return True

def parse():
    connection, cursor = connect('news.db')
    if not connection or not cursor:
        print("[parse] Не удалось подключиться к базе данных.")
        return

    create_news_table(cursor, connection)
    create_categories_table(cursor, connection)
    create_university_table(cursor, connection)
    create_users_table(cursor, connection)
    create_user_cat_table(cursor, connection)

    university_id = get_university_id(cursor, "МИФИ")
    last_link = get_last_link(cursor, university_id)
    print(f"Последняя сохраненная ссылка МИФИ: {last_link}")

    base_url = "https://mephi.ru/press/news"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    page = 0
    max_pages = 10

    while page < max_pages:
        if page == 0:
            url = base_url
        else:
            url = f"{base_url}?page={page}"
        print(f"Парсинг страницы {page}: {url}")
        has_next = fetch_page(url, headers, cursor, connection, last_link, university_id)

        if not has_next:
            break
        page += 1

    print("\nСодержимое базы после парсинга:")
    print_all_rows(cursor)

    connection.close()

if __name__ == "__main__":
    parse()