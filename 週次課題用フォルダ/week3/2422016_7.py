import pandas as pd

# データの読み込み
df = pd.read_csv('Wine Quality Red.csv', sep=',')

#データの5~10行目を表示
print(df[5:11])