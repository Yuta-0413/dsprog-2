import requests
from datetime import datetime

# 東京都の地域ID
area_id = "130000"
forecast_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_id}.json"

try:
    # 天気データを取得
    response = requests.get(forecast_url)
    response.raise_for_status()  # HTTPエラーのチェック

    # JSONデータをパース
    forecast_data = response.json()

    # 当日の天気データを抽出
    today_date = datetime.now().strftime("%Y-%m-%d")  # 今日の日付
    print(f"東京都の天気情報（{today_date}）")

    # 時系列データを処理
    for area in forecast_data:
        if "timeSeries" in area:
            time_series = area["timeSeries"]
            for series in time_series:
                if "areas" in series:
                    for region in series["areas"]:
                        if region["area"]["code"] == "130010":  # 東京地方のエリアコード
                            # 該当日付の天気情報を取得
                            times = series["timeDefines"]
                            weathers = region["weathers"]
                            for i, time in enumerate(times):
                                if today_date in time:  # 今日の日付に一致するデータのみ
                                    print(f"時刻: {time}")
                                    print(f"天気: {weathers[i]}")
                                    print("-" * 30)

except requests.RequestException as e:
    print(f"データ取得中にエラーが発生しました: {e}")
except KeyError as e:
    print(f"データの解析中にエラーが発生しました: {e}")