import numpy as np
import pandas as pd

#データの読み込み
data1=pd.read_csv("週次課題用フォルダ/week4/Users.csv")
data2=pd.read_csv("週次課題用フォルダ/week4/Items.csv")
data3=pd.read_csv("週次課題用フォルダ/week4/Orders.csv")

#データの結合
data=pd.merge(data2,data3,on="item_id",how="inner")

#各ユーザーの平均購入金額を計算
data["price"]=data["item_price"]*data["order_num"]
data=data.groupby("user_id")["price"].mean().reset_index()
data=data.sort_values("price",ascending=False)

#最も平均購入金額の高いユーザーを抽出
data=data.head(1)

#結果の出力
print(data)