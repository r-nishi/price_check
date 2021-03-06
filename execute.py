# -*- coding: utf-8 -*-

"""
晴れる屋のNM価格をWebスクレイピングして取得するプログラム
"""

from bs4 import BeautifulSoup
import urllib
from pprint import pprint
import requests
import watchtower, logging
import boto3
import pymysql
import rds_config as RDS


def output_to_aws(message):
    """
    CloudWatchLogsにログを出力する処理

    Parameters
    ----------
    message : basestring
    """
    boto3.Session(profile_name='default')
    # ログレベルをinfoにする
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.addHandler(
        watchtower.CloudWatchLogHandler(
            log_group='price_check_logs',  # ロググループを指定
            stream_name='hareruya'  # ログストリームを指定
        )
    )
    logger.info(message)


# 価格を調べたいカードのURLを入力
target_url = 'https://www.hareruyamtg.com/ja/products/detail/69814'

# リンク先をデコード
html = urllib.request.urlopen(target_url).read().decode('utf-8')

# BeautifulSoupのインスタンスを生成
soup = BeautifulSoup(html, 'html.parser')

# カード名を取得
card_name = soup.find("h2", class_="goods_name_").string

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

message = card_name + 'の値段は' + str(max(output_list)) + ' 〜 ' + str(min(output_list)) + 'です'

pprint(message)

# アクセストークン
access_token = ''

# LINEへ通知
headers = {'Authorization': 'Bearer ' + access_token}
payload = {'message': message}
requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)

# AWS
output_to_aws(message)

# RDS
con = pymysql.connect(
        host=RDS.rds_host,
        user=RDS.db_user,
        password=RDS.db_password,
        db=RDS.db_name,
        cursorclass=pymysql.cursors.DictCursor
)

try:
    with con.cursor() as cur:
        sql = 'INSERT INTO daily_price (id, shop_name, card_name, price_maximum, price_minimum) VALUES (%s, %s, %s, %s, %s)'
        cur.execute(sql, (1, "晴れる屋", card_name, str(max(output_list)), str(min(output_list))))
        con.commit()

        result = cur.fetchall()
        print(result)
except:
    print('Error')
