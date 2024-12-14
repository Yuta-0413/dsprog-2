import sqlite3
import csv
import os
import hashlib

#ファイルのハッシュを計算する関数
def calculate_file_hash(file_path):
    hasher = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        return None

#データベースとテーブルの作成
def create_db():
    db_path = "個人課題3/weather.db"
    #データベースに接続（存在しない場合は新規作成）
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    #weather テーブルを作成
    c.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY,  -- 通し番号（主キー）
            area_name TEXT,          -- 地域名
            date TEXT,               -- 日付
            weather_desc TEXT        -- 天気の説明
        )
    """)
    conn.commit()
    conn.close()
    print(f"データベース {db_path} を作成または既存のものを使用します。")

#CSVが変更されていた場合にデータベースを再作成
def reset_db_if_csv_changed():
    db_path = "個人課題3/weather.db"
    csv_path = "個人課題3/weather.csv"
    hash_file = "個人課題3/weather.csv.hash"

    #現在のCSVファイルのハッシュを計算
    current_hash = calculate_file_hash(csv_path)

    if current_hash is None:
        print(f"CSVファイルが見つかりません: {csv_path}")
        return False

    #以前のハッシュを読み取る
    previous_hash = None
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            previous_hash = f.read().strip()

    #ハッシュが異なる場合、データベースを削除して再作成
    if current_hash != previous_hash:
        print("CSVファイルの内容が変更されました。データベースをリセットします。")
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"既存のデータベース {db_path} を削除しました。")
        create_db()
        #現在のハッシュを保存
        with open(hash_file, "w") as f:
            f.write(current_hash)
        return True

    print("CSVファイルの内容に変更はありません。")
    return False

#CSVからデータをSQLiteデータベースに格納
def import_csv_to_db():
    db_path = "個人課題3/weather.db"
    csv_path = "個人課題3/weather.csv"

    #CSVファイルの存在を確認
    if not os.path.exists(csv_path):
        print(f"CSVファイルが見つかりません: {csv_path}")
        return

    #データベースに接続
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    #CSVを開いてデータをインポート
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            try:
                #各行をデータベースに挿入
                c.execute("""
                    INSERT INTO weather (id, area_name, date, weather_desc)
                    VALUES (?, ?, ?, ?)
                """, (int(row[0]), row[1], row[2], row[3]))
            except sqlite3.IntegrityError as e:
                print(f"重複データのためスキップ: {row}")
            except Exception as e:
                print(f"エラーが発生しました: {e} 行: {row}")

    conn.commit()
    conn.close()
    print("CSVからデータベースへの格納が完了しました。")

#データベースの内容を表示
def show_db_contents():
    db_path = "個人課題3/weather.db"

    #データベースが存在するか確認
    if not os.path.exists(db_path):
        print(f"データベースが見つかりません: {db_path}")
        return

    #データベース接続
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    #データベース内の全データを取得
    c.execute("SELECT * FROM weather")
    rows = c.fetchall()
    conn.close()

    #データを表示
    if rows:
        print("データベースの内容:")
        for row in rows:
            print(row)
    else:
        print("データベースにデータがありません。")

#メイン関数
if __name__ == "__main__":
    csv_changed = reset_db_if_csv_changed()
    if csv_changed:
        import_csv_to_db()
    show_db_contents()