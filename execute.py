# -*- coding: utf-8 -*-

"""
晴れる屋のNM価格をWebスクレイピングして取得するプログラム
"""

from bs4 import BeautifulSoup
import urllib.request
from pprint import pprint
import requests

# 価格を調べたいカードのURLを入力
target_url = 'https://www.hareruyamtg.com/ja/products/detail/69814'

# リンク先をデコード
html = urllib.request.urlopen(target_url).read().decode('utf-8')

# BeautifulSoupのインスタンスを生成
soup = BeautifulSoup(html, 'html.parser')

# idから価格表を取得
price_table = soup.find(id="priceTable-EN")
# div classからカードの状態ごとの価格を詳しく取得
price_list = price_table.find_all("div", class_="col-xs-3 ng-star-inserted")

# 3番目がNM価格
# 将来的には全ての価格を比較して最高値と最安値の2つを取るように修正する
nm_price = price_list[2].string

# 出力用のリスト
output_list = []

for price in price_list:
    if len(price) > 0:

        # 価格を除外
        if price.contents[0] == '価格':
            continue

        # ¥と,を削除してリストに入れる
        output_list.append(int(price.contents[0].replace(',', '').replace('￥', '')))

message = str(max(output_list)) + ' 〜 ' + str(min(output_list))

pprint(message)

# アクセストークン
access_token = ''

# LINEへ通知
headers = {'Authorization': 'Bearer ' + access_token}
payload = {'message': message}
requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
