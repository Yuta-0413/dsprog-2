import pandas as pd

# データの読み込み
df = pd.read_csv('Wine Quality Red.csv', sep=',')

#quality列の値が6以上のデータをqualityの値が高い順に表示
print(df[df["quality"] >= 6].sort_values("quality", ascending=False))