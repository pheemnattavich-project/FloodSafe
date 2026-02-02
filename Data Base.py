import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime

DB_FILE = "thaiwater_wl.db"
URL = "https://www.thaiwater.net/water/wl"

# -----------------------------------
# 1) ตั้งค่า Database
# -----------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS water_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_name TEXT,
        measure_datetime TEXT,
        water_level TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

# -----------------------------------
# 2) Scrape ข้อมูลจากหน้าเว็บ ThaiWater
# -----------------------------------
def scrape_thaiwater():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    # หน้าเว็บมีตาราง <table> ที่แสดงระดับน้ำ
    table = soup.find("table")
    if not table:
        print("ไม่พบตารางข้อมูลบนหน้าเว็บนี้")
        return []

    data_rows = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 4:
            station = cols[0].text.strip()
            datetime_str = cols[1].text.strip()
            water_level = cols[2].text.strip()
            status = cols[3].text.strip()
            data_rows.append((station, datetime_str, water_level, status))
    return data_rows

# -----------------------------------
# 3) เก็บข้อมูลลง Database
# -----------------------------------
def save_to_db(data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for (station, dt, level, stat) in data:
        cursor.execute("""
        INSERT INTO water_data (station_name, measure_datetime, water_level, status)
        VALUES (?, ?, ?, ?)
        """, (station, dt, level, stat))
    conn.commit()
    conn.close()

# -----------------------------------
# 4) เรียกดูข้อมูลจาก DB
# -----------------------------------
def get_all_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM water_data ORDER BY measure_datetime DESC")
    result = cursor.fetchall()
    conn.close()
    return result

# -----------------------------------
# 5) ตัวอย่างการทำงาน
# -----------------------------------
if __name__ == "__main__":
    init_db()

    print("กำลังดึงข้อมูลจาก ThaiWater ...")
    scraped = scrape_thaiwater()
    if scraped:
        print(f"เจอรายการ {len(scraped)} รายการ")
        save_to_db(scraped)
        print("บันทึกข้อมูลลงฐานข้อมูลเรียบร้อย")

    print("\nข้อมูลล่าสุดที่เก็บไว้:")
    rows = get_all_data()
    for row in rows[:10]:
        print(row)
