# -*- coding: utf-8 -*-

"""
晴れる屋のNM価格をWebスクレイピングして取得するプログラム
"""

from bs4 import BeautifulSoup
import urllib.request
from pprint import pprint

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
print(price_list[2].string)
