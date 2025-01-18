import requests
from bs4 import BeautifulSoup

def get_current_weather():
    # tenki.jp の天気情報ページ URL
    forecast_url = "https://tenki.jp/forecast/3/16/4410/13212/"
    try:
        # ページのHTMLを取得
        response = requests.get(forecast_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # 現在の天気情報を取得
        current_weather = soup.find('p', class_='weather-telop')
        if not current_weather:
            return "現在の天気情報が見つかりませんでした"
        # 現在の天気情報のテキストを取得
        weather_summary = current_weather.get_text(strip=True)
        return f"現在の天気: {weather_summary}"
    except Exception as e:
        return f"天気情報の取得に失敗しました: {e}"

if __name__ == "__main__":
    weather_info = get_current_weather()
    print(weather_info)