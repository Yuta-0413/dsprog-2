import pandas as pd

#データの読み込み
data = pd.read_csv("週次課題用フォルダ/week4/Items.csv")

#item_idが101の商品情報を取得
target_item = data[data["item_id"] == 101].iloc[0]

#商品の基本情報
small_category = target_item["small_category"]
big_category = target_item["big_category"]
target_price = target_item["item_price"]
target_pages = target_item["pages"]

#推薦候補リストを初期化
recommendations = data.copy()

#ルール1: 小カテゴリ→大カテゴリの順でカテゴリが近いものを優先
recommendations["rule1_rank"] = 0
recommendations.loc[recommendations["small_category"] == small_category, "rule1_rank"] += 1
recommendations.loc[recommendations["big_category"] == big_category, "rule1_rank"] += 1

#ルール2: カテゴリが同じ場合、価格が近いものを優先
recommendations["price_diff"] = abs(recommendations["item_price"] - target_price)

#ルール3: カテゴリと価格が同じ場合、ページ数が近いものを優先
recommendations["page_diff"] = abs(recommendations["pages"] - target_pages)

#推薦スコアを計算
#rule1_rankを優先し、次に価格差、最後にページ差で並べ替え
recommendations = recommendations.sort_values(
    by=["rule1_rank", "price_diff", "page_diff"],
    ascending=[False, True, True]
)

# 推薦候補からitem_idを抽出（自身を除外）
final_recommendations = recommendations[recommendations["item_id"] != 101]["item_id"].tolist()

#上位3件を取得
top_3_recommendations = final_recommendations[:3]

#結果を整形して出力
print(f"推薦候補1のitem_id: {top_3_recommendations[0] if len(top_3_recommendations) > 0 else 'なし'}")
print(f"推薦候補2のitem_id: {top_3_recommendations[1] if len(top_3_recommendations) > 1 else 'なし'}")
print(f"推薦候補3のitem_id: {top_3_recommendations[2] if len(top_3_recommendations) > 2 else 'なし'}")