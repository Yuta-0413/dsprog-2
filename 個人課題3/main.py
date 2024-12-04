import flet as ft
import requests

#地域リストを取得
def get_area_list():
    try:
        response = requests.get("http://www.jma.go.jp/bosai/common/const/area.json")
        response.raise_for_status()
        return response.json()["offices"]
    except Exception as e:
        raise Exception(f"地域リストの取得に失敗しました: {e}")

#地方ごとの地域IDのマッピング
REGION_MAPPING = {
    "北海道地方": ["011000", "012000", "013000", "014000", "015000", "016000", "017000"],
    "東北地方": ["020000", "030000", "040000", "050000", "060000", "070000"],
    "関東地方": ["080000", "090000", "100000", "110000", "120000", "130000", "140000", "190000", "200000"],
    "東海地方": ["210000", "220000", "230000", "240000"],
    "北陸地方": ["150000", "160000", "170000", "180000"],
    "近畿地方": ["250000", "260000", "270000", "280000", "290000", "300000"],
    "中国地方(山口を除く)": ["310000", "320000", "330000", "340000"],
    "四国地方": ["360000", "370000", "380000", "390000"],
    "九州地方北部(山口含む)": ["350000", "400000", "410000", "420000", "430000", "440000"],
    "九州地方南部・奄美": ["450000", "460040", "460100"],
    "沖縄地方":["471000", "472000", "473000", "474000"],
}

#地方分けに従ってデータを整理
def group_by_region_fixed(area_data):
    regions = {region: [] for region in REGION_MAPPING.keys()}
    for area_id, area_info in area_data.items():
        for region, ids in REGION_MAPPING.items():
            if area_id in ids:
                regions[region].append((area_id, area_info["name"]))
                break
    return regions

#天気データを取得
def get_weather_data(area_id):
    try:
        response = requests.get(f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_id}.json")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"天気情報の取得に失敗しました: {e}")

#天気の内容に基づくアイコンのマッピング
def get_weather_icon(weather):
    if "晴" in weather:
        return ft.icons.WB_SUNNY
    elif "曇" in weather:
        return ft.icons.CLOUD
    elif "雨" in weather:
        return ft.icons.UMBRELLA
    elif "雪" in weather:
        return ft.icons.AC_UNIT
    else:
        return ft.icons.HELP_OUTLINE  #不明な天気用アイコン

#天気データを解析
def parse_weather(weather_data):
    try:
        time_series = weather_data[0]["timeSeries"][0]
        weather_forecast = time_series["areas"][0]["weathers"]
        dates = time_series["timeDefines"]
        #アイコンを追加してリストにする
        return [(date, weather, get_weather_icon(weather)) for date, weather in zip(dates, weather_forecast)]
    except (IndexError, KeyError) as e:
        return []

#ページのサイズを設定する関数
def set_page_size(page: ft.Page, width: int, height: int):
    page.window_width = width
    page.window_height = height

#メインアプリケーション
def main(page: ft.Page):
    page.title = "簡易天気予報アプリ"
    page.scroll = "adaptive"
    set_page_size(page, width=1366, height=768)

    #地域データを取得
    try:
        area_data = get_area_list()
    except Exception as e:
        page.add(ft.Text(f"地域データの取得に失敗しました: {e}", color="red"))
        return

    #地方ごとにデータを整理
    grouped_areas = group_by_region_fixed(area_data)

    #地方リスト
    region_names = list(grouped_areas.keys())

    #天気情報を表示するコンテナ
    weather_container = ft.Column(scroll="adaptive")

    #天気予報を表示する関数
    def show_weather(area_id):
        weather_container.controls.clear()
        if not area_id:
            weather_container.controls.append(ft.Text("地域を選択してください。"))
            page.update()
            return
        try:
            #天気データを取得
            weather_data = get_weather_data(area_id)
            forecast = parse_weather(weather_data)
            #地域名
            area_name = next(
                (name for areas in grouped_areas.values() for id_, name in areas if id_ == area_id),
                "不明"
            )
            #天気情報を表示
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

    #地方を選択したときに表示される地域リストを作成する関数
    def show_region_areas(selected_index):
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

        #サイドバーの内容を更新
        sidebar_content.controls.clear()
        sidebar_content.controls.append(ft.Text(f"{region_name}の地域一覧", style="headlineSmall", weight="bold"))
        sidebar_content.controls.append(area_list)
        page.update()

    #NavigationRailの項目を作成
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

    #初期の地域リスト
    sidebar_content = ft.Column()

    #ページのレイアウト
    page.add(
        ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        #地方選択サイドバー
                        ft.Container(
                            content=nav_rail,
                            height=600,
                            bgcolor=ft.colors.BLACK12,
                            alignment=ft.alignment.top_center,
                        ),
                        ft.VerticalDivider(width=1),  # 区切り線
                        #地域リストサイドバー
                        ft.Container(
                            content=sidebar_content,
                            bgcolor=ft.colors.BLACK12,
                            padding=ft.padding.only(top=20),
                            width=250,
                            alignment=ft.alignment.top_left,
                        ),
                        ft.VerticalDivider(width=1),  #区切り線
                        #天気情報表示エリア
                        ft.Container(
                            content=weather_container,
                            expand=True,
                            padding=ft.padding.only(top=20),
                            alignment=ft.alignment.top_left,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                ),
            ],
            alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )
    )


    #初期表示: 最初の地方を選択
    show_region_areas(0)

#アプリケーションを実行
if __name__ == "__main__":
    ft.app(target=main)