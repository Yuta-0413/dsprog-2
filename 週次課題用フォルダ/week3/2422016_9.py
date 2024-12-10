import pandas as pd

# データの読み込み
df = pd.read_csv('Wine Quality Red.csv', sep=',')

#qualityの値ごとにカテゴリーごとの平均を表示
df.groupby("quality").mean()