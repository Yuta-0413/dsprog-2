import numpy as np
import pandas as pd

#データの読み込み
data1=pd.read_csv("週次課題用フォルダ/week4/Users.csv")
data2=pd.read_csv("週次課題用フォルダ/week4/Items.csv")
data3=pd.read_csv("週次課題用フォルダ/week4/Orders.csv")

#データの結合
data=pd.merge(data2,data3,on="item_id",how="inner")

#各注文の購入金額を計算
data["price"]=data["item_price"]*data["order_num"]

#最も高い購入金額の注文を抽出
data=data.groupby("order_id")["price"].sum().reset_index()
data=data.sort_values("price",ascending=False)

#結果の出力
print(data.head(1))