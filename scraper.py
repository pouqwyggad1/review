import sqlite3
import requests
from bs4 import BeautifulSoup

ORIGINAL_URL = 'https://askgeek.io/ru/cpus/list?page='

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def month_to_number(month_str):
    months = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
        'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }
    return months.get(month_str, '00')

def convert_date(release_date):
    if release_date:
        if "Q" in release_date and "'" in release_date:
            quarter, year = release_date.split("'")
            year = "20" + year
            quarter_to_month = {
                "Q1": "01.01",
                "Q2": "01.04",
                "Q3": "01.07",
                "Q4": "01.10",
            }
            month_day = quarter_to_month.get(quarter, "01.01")
            return f"{month_day}.{year}"

        parts = release_date.split()
        if len(parts) == 3:
            day, month_str, year = parts
            day = day.zfill(2)
            month = month_to_number(month_str)
            return f"{day}.{month}.{year}"

    return None

def parse_int(value):
    try:
        if value.strip() == "":
            return None
        return int(value)
    except (ValueError, TypeError):
        return None

def parse_frequency(value):
    if value and value.strip() != "":
        try:
            value = value.replace('ГГц', '').replace('GHz', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return None
    return None

def scrape_page(page):
    url = ORIGINAL_URL + str(page)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.select('table tbody tr')

    processors = []

    for row in rows:
        cols = row.find_all('td')
        if not cols:
            continue

        rank = parse_int(cols[0].text.strip())
        name = cols[1].text.strip()
        category = cols[2].text.strip()
        release_date = cols[4].text.strip() if cols[4].text.strip() else "None"

        if release_date and "Q" in release_date:
            release_date = convert_date(release_date)
        elif release_date and " " in release_date:
            release_date = convert_date(release_date)

        specs = cols[5].find('ul', class_='specs')
        socket, cores, max_frequency = None, None, None

        if specs:
            for spec in specs.find_all('li'):
                text = spec.text.strip()
                if 'Сокет:' in text:
                    socket = text.replace('Сокет:', '').strip()
                elif 'Кол-во ядер:' in text:
                    cores = text.replace('Кол-во ядер:', '').strip()
                elif 'Макс. частота:' in text:
                    max_frequency = text.replace('Макс. частота:', '').strip()

        cores = parse_int(cores)
        max_frequency = parse_frequency(max_frequency)

        if not socket:
            socket = 'None'

        if not max_frequency:
            max_frequency = None

        link = "https://askgeek.io" + cols[1].find('a')['href']

        processors.append((rank, name, category, release_date, socket, cores, max_frequency, link))

    return processors

def scrape_all_pages():
    all_processors = []
    for page in range(1, 11):
        print(f"Scraping page #{page}")
        all_processors.extend(scrape_page(page))
    return all_processors

def save_to_sql(processors):
    connect = sqlite3.connect('/app/processors.db')
    cursor = connect.cursor()

    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS processors (
        rank INTEGER,
        name TEXT,
        category TEXT,
        release_date TEXT,
        socket TEXT,
        cores INTEGER,
        max_frequency REAL,
        link TEXT
    )
    ''')

    cursor.executemany(''' 
    INSERT INTO processors (rank, name, category, release_date, socket, cores, max_frequency, link) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', processors)

    connect.commit()
    connect.close()
    print("Successful scraping into processors.db")

if __name__ == "__main__":
    processors = scrape_all_pages()
    save_to_sql(processors)
