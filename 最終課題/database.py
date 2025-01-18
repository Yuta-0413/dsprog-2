import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3
import time
import schedule

#SQLite DBファイル名
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

#データ取得:東京都の天気情報
def get_weather():
    forecast_url = "https://www.jma.go.jp/bosai/forecast/#area_type=offices&area_code=130000"
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # "東京地方" 部分を検索する
        tokyo_weather_section = soup.find('div', class_='forecast-point-name', string="東京地方")
        if not tokyo_weather_section:
            return "天気情報が見つかりません"

        # "東京地方" に関連付けられた天気情報を取得
        parent_div = tokyo_weather_section.find_parent('div', class_='forecast-table')
        weather_info = parent_div.find('p', class_='weather-telop').text.strip()
        return weather_info

    except Exception as e:
        return f"天気情報取得エラー: {e}"

#データを取得してDBに追加
def fetch_and_store_data():
    #現在時刻と日付を取得
    now = datetime.now()
    fetch_time = now.strftime("%H:%M:%S")
    today_date = now.strftime("%Y-%m-%d")
    #天気と運行状況を取得
    weather = get_weather()
    delay_status = get_monorail_status()
    #データをDBに挿入
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

def schedule_tasks():
    #5:00～23:00の間、1時間ごとに実行
    for hour in range(5, 24):
        time_str = f"{hour:02d}:00"
        schedule.every().day.at(time_str).do(fetch_and_store_data)
    #24:00（=翌日00:00）のスケジュールを追加
    schedule.every().day.at("00:00").do(fetch_and_store_data)

    print("スケジュールを設定しました:5:00～24:00の間、1時間ごとに実行します。")

#スケジュール実行ループ
if __name__ == "__main__":
    create_table()
    schedule_tasks()

    print("スケジュール実行を開始します...")
    while True:
        schedule.run_pending()
        time.sleep(1)