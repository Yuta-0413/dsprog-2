import flet as ft
import requests

# 地域リストを取得する関数
def get_area_list():
    try:
        response = requests.get('http://www.jma.go.jp/bosai/common/const/area.json')
        response.raise_for_status()
        return response.json()["offices"]
    except Exception as e:
        raise Exception(f"地域リストの取得に失敗しました: {e}")

# 天気情報を取得する関数
def get_weather_data(area_id):
    try:
        response = requests.get(f'https://www.jma.go.jp/bosai/forecast/data/forecast/{area_id}.json')
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"天気情報の取得に失敗しました: {e}")

# 天気情報を解析する関数
def parse_weather(weather_data):
    try:
        time_series = weather_data[0]["timeSeries"][0]
        weather_forecast = time_series["areas"][0]["weathers"]
        dates = time_series["timeDefines"]
        return list(zip(dates, weather_forecast))
    except (IndexError, KeyError) as e:
        return []

# メイン関数 (Flet アプリケーション)
def main(page: ft.Page):
    page.title = "気象庁APIを利用した天気予報アプリ"
    page.scroll = "adaptive"

    # 地域リストを取得
    try:
        area_list = get_area_list()
    except Exception as e:
        page.add(ft.Text(value=f"地域リストの取得に失敗しました: {e}", color="red"))
        return

    # 地域選択用のドロップダウン
    dropdown = ft.Dropdown(
        label="地域を選択してください",
        options=[ft.dropdown.Option(key=code, text=info["name"]) for code, info in area_list.items()],
        on_change=lambda e: show_weather(e.control.value),
    )

    # 天気情報表示用のコンテナ
    weather_container = ft.Column()

    # ページに要素を追加
    page.add(dropdown, weather_container)

    # 天気情報を表示する関数
    def show_weather(area_id):
        weather_container.controls.clear()

        if not area_id:
            return

        try:
            # 天気情報を取得
            weather_data = get_weather_data(area_id)
            forecast = parse_weather(weather_data)

            # 地域名を取得
            area_name = area_list[area_id]["name"]

            # 天気情報を表示
            weather_container.controls.append(ft.Text(value=f"{area_name}の天気予報", style="headlineLarge", weight="bold"))
            for date, weather in forecast:
                weather_container.controls.append(
                    ft.ListTile(
                        title=ft.Text(value=date),
                        subtitle=ft.Text(value=weather),
                        leading=ft.Icon(ft.icons.WB_SUNNY if "晴" in weather else ft.icons.WB_CLOUDY),
                    )
                )
        except Exception as e:
            weather_container.controls.append(ft.Text(value=f"天気情報の取得に失敗しました: {e}", color="red"))

        # ページを更新
        page.update()

# アプリケーションを実行
if __name__ == "__main__":
    ft.app(target=main)