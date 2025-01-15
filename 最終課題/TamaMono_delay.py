import requests
from bs4 import BeautifulSoup

#京王線の運行状況のURL
TamaMono_URL = 'https://transit.yahoo.co.jp/diainfo/156/0'

#Requestsを利用してWebページを取得する
TamaMono_Requests = requests.get(TamaMono_URL)

# BeautifulSoupを利用してWebページを解析する
TamaMono_Soup = BeautifulSoup(TamaMono_Requests.text, 'html.parser')

#.findでtroubleクラスのddタグを探す
if TamaMono_Soup.find('dd',class_='trouble'):
    message = '多摩都市モノレールは遅延しています'
else:
    message = '多摩都市モノレールは通常運転です'

print(message)