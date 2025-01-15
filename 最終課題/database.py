import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3
import time

# SQLite DBファイル名
DB_NAME = "最終課題/transport_weather.db"

# テーブル作成
def create_table():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transport_weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                fetch_time TEXT,
                weather TEXT,
                delay_status TEXT
            )
        ''')
        conn.commit()

# データをDBに追加する関数
def insert_data(date, fetch_time, weather, delay_status):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transport_weather (date, fetch_time, weather, delay_status)
            VALUES (?, ?, ?, ?)
        ''', (date, fetch_time, weather, delay_status))
        conn.commit()

# データ取得: 多摩都市モノレールの運行状況
def get_monorail_status():
    TamaMono_URL = 'https://transit.yahoo.co.jp/diainfo/156/0'
    try:
        TamaMono_Requests = requests.get(TamaMono_URL)
        TamaMono_Soup = BeautifulSoup(TamaMono_Requests.text, 'html.parser')
        time.sleep(1)
        if TamaMono_Soup.find('dd', class_='trouble'):
            return '多摩都市モノレールは遅延しています'
        else:
            return '多摩都市モノレールは通常運転です'
    except Exception as e:
        return f"運行状況取得エラー: {e}"

# データ取得: 東京都の天気情報
def get_weather():
    area_id = "130000"
    forecast_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_id}.json"
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()
        forecast_data = response.json()
        today_date = datetime.now().strftime("%Y-%m-%d")
        for area in forecast_data:
            if "timeSeries" in area:
                time_series = area["timeSeries"]
                for series in time_series:
                    if "areas" in series:
                        for region in series["areas"]:
                            if region["area"]["code"] == "130010":
                                times = series["timeDefines"]
                                weathers = region["weathers"]
                                for i, time in enumerate(times):
                                    if today_date in time:
                                        return weathers[i]
    except Exception as e:
        return f"天気情報取得エラー: {e}"

# データを取得してDBに追加
def fetch_and_store_data():
    # 現在時刻と日付を取得
    now = datetime.now()
    fetch_time = now.strftime("%H:%M:%S")
    today_date = now.strftime("%Y-%m-%d")

    # 天気と運行状況を取得
    weather = get_weather()
    delay_status = get_monorail_status()

    # データをDBに挿入
    insert_data(today_date, fetch_time, weather, delay_status)
    print("データをDBに保存しました:")
    print(f"日付: {today_date}, 時刻: {fetch_time}, 天気: {weather}, 遅延: {delay_status}")

# DB内のデータを表示する関数
def display_db_data():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transport_weather")
        rows = cursor.fetchall()
        print("DB内のデータ:")
        for row in rows:
            print(row)

# メイン処理
if __name__ == "__main__":
    create_table()
    fetch_and_store_data()
    display_db_data()