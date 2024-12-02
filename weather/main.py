import flet as ft
import requests

# 地域リストを取得する関数
def get_area_list():
    """地域リストを取得する関数。"""
    try:
        response = requests.get("http://www.jma.go.jp/bosai/common/const/area.json")
        response.raise_for_status()
        return response.json()["offices"]
    except Exception as e:
        raise Exception(f"地域リストの取得に失敗しました: {e}")

# 地方ごとにデータを整理する関数
def group_by_region(area_data):
    """地域データを地方ごとに分類する。"""
    regions = {}
    for area_id, area_info in area_data.items():
        region = area_info["parent"]  # 地方名を取得
        if region not in regions:
            regions[region] = []
        regions[region].append((area_id, area_info["name"]))  # 地域IDと名前を追加
    return regions

# 天気データを取得する関数
def get_weather_data(area_id):
    """天気データを取得する関数。"""
    try:
        response = requests.get(f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_id}.json")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"天気情報の取得に失敗しました: {e}")

# 天気の内容に基づくアイコンのマッピング
def get_weather_icon(weather):
    """天気予報の内容に基づいてアイコンを選択する。"""
    if "晴" in weather:
        return ft.icons.WB_SUNNY
    elif "曇" in weather:
        return ft.icons.CLOUD
    elif "雨" in weather:
        return ft.icons.UMBRELLA
    elif "雪" in weather:
        return ft.icons.AC_UNIT
    else:
        return ft.icons.HELP_OUTLINE  # 不明な天気用アイコン

# 天気データを解析する関数
def parse_weather(weather_data):
    """天気データを解析して日付、予報、アイコンを返す。"""
    try:
        time_series = weather_data[0]["timeSeries"][0]
        weather_forecast = time_series["areas"][0]["weathers"]
        dates = time_series["timeDefines"]
        # アイコンを追加してリストにする
        return [(date, weather, get_weather_icon(weather)) for date, weather in zip(dates, weather_forecast)]
    except (IndexError, KeyError) as e:
        return []

# メインアプリケーション
def main(page: ft.Page):
    page.title = "簡易天気予報アプリ"
    page.scroll = "adaptive"

    # 地域データを取得
    try:
        area_data = get_area_list()
    except Exception as e:
        page.add(ft.Text(f"地域データの取得に失敗しました: {e}", color="red"))
        return

    # 地方ごとにデータを整理
    grouped_areas = group_by_region(area_data)

    # 地方リスト
    region_names = list(grouped_areas.keys())

    # 天気情報を表示するコンテナ
    weather_container = ft.Column(scroll="adaptive")

    # 天気予報を表示する関数
    def show_weather(area_id):
        """選択した地域の天気予報を表示する。"""
        weather_container.controls.clear()
        if not area_id:
            weather_container.controls.append(ft.Text("地域を選択してください。"))
            page.update()
            return
        try:
            # 天気データを取得
            weather_data = get_weather_data(area_id)
            forecast = parse_weather(weather_data)
            # 地域名
            area_name = next(
                (name for areas in grouped_areas.values() for id_, name in areas if id_ == area_id),
                "不明"
            )
            # 天気情報を表示
            weather_container.controls.append(ft.Text(f"{area_name}の天気予報", style="headlineLarge", weight="bold"))
            if not forecast:
                weather_container.controls.append(ft.Text("天気情報が見つかりません。", color="red"))
            for date, weather, icon in forecast:
                weather_container.controls.append(
                    ft.ListTile(
                        title=ft.Text(date),
                        subtitle=ft.Text(weather),
                        leading=ft.Icon(icon),  # 天気アイコンを追加
                    )
                )
        except Exception as e:
            weather_container.controls.append(ft.Text(f"天気情報の取得に失敗しました: {e}", color="red"))
        page.update()

    # 地方を選択したときに表示される地域リストを作成する関数
    def show_region_areas(selected_index):
        """選択した地方の地域リストを表示する。"""
        region_name = region_names[selected_index]
        areas = grouped_areas[region_name]

        # 地域リストを作成
        area_list = ft.Column(
            controls=[
                ft.ListTile(
                    title=ft.Text(area_name),
                    on_click=lambda e, id_=area_id: show_weather(id_),
                )
                for area_id, area_name in areas
            ],
            spacing=10,
        )

        # サイドバーの内容を更新
        sidebar_content.controls.clear()
        sidebar_content.controls.append(ft.Text(f"{region_name}の地域一覧", style="headlineSmall", weight="bold"))
        sidebar_content.controls.append(area_list)
        page.update()

    # NavigationRailの項目を作成
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.LIST_ALT,
                selected_icon=ft.icons.CHECKLIST,
                label=region_name,
            )
            for region_name in region_names
        ],
        on_change=lambda e: show_region_areas(e.control.selected_index),
    )

    # 初期の地域リスト
    sidebar_content = ft.Column()

    # レイアウト
    page.add(
        ft.Row(
            controls=[
                # NavigationRail (左端の地方選択サイドバー)
                ft.Container(
                    content=nav_rail,
                    height=600,  # 固定高さを設定
                    bgcolor=ft.colors.BLACK12,
                ),
                ft.VerticalDivider(width=1),  # 区切り線
                # サイドバー (地域リスト表示)
                ft.Container(
                    content=sidebar_content,
                    bgcolor=ft.colors.BLACK12,
                    padding=10,
                    width=250,
                ),
                ft.VerticalDivider(width=1),  # サイドバーとコンテンツの区切り
                # 天気情報表示エリア
                ft.Container(
                    content=weather_container,
                    expand=True,
                    padding=20,
                ),
            ],
            expand=True,
        )
    )

    # 初期表示: 最初の地方を選択
    show_region_areas(0)

# アプリケーションを実行
if __name__ == "__main__":
    ft.app(target=main)