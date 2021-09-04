import sys
import os
import traceback
import requests
from bs4 import BeautifulSoup
from backend.app.func.notify import LINENotifyBot
from backend.app.settings.logging_prd import logging_setting
from backend.app.settings.config_file import CHECK_URL, LINE_NOTIFY_SANRES_ACCESS_TOKEN
from backend.app.func.connect_firestorage import upload_bucket_file, download_bucket_file

# ログの記録するフォーマットを決める
logger = logging_setting("tmp")
# 比較用テキストファイル
logfile_name = "tmp/sanres_log.txt"
# チェックしたいURL
url = CHECK_URL
# LINE notifyのアクセストークン
bot = LINENotifyBot(LINE_NOTIFY_SANRES_ACCESS_TOKEN)
# プログラムからのアクセスを弾かれないようにヘッダー情報を追加
headers_dic = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}
try:
    # HTMLを取得する
    # html = urllib.request.urlopen(url)
    html = requests.get(url, headers=headers_dic)
    # HTMLのステータスコード（正常に取得できたかどうか）を記録する
    logger.info("html content" + str(html.content))
    logger.info('HTTP STATUS CODE: ' + str(html.status_code))
except:
    # 取得に失敗した場合もLINEに通知してログを取る
    bot.send('URLの取得に失敗しました')
    # 念の為強制終了
    sys.exit(1)
# 取得したリクエストをパースする
soup = BeautifulSoup(html.content, "html.parser")
logger.info("get Beautiful soup" + str(soup))
# HTMLの中からaタグのみを抽出
# tags = soup.find_all("a")
links = list()
# 前回取ったリンク
oldlinks = set()
# 今回とったリンク
newlinks = set()
# for tag in tags:
#     # aタグからリンクのURLのみを取り出す。
#     links.append(tag.get('href'))
try:
    if os.path.exists(str(logfile_name)):
        # 前回取得したリンクをファイルから読み込む
        with open(logfile_name, 'r') as f:
            # 前回のリンクにセット
            oldlinks = set(f)
            # reader = csv.reader(f)
            # for row in reader:
            #     oldlinks = set(row)
            logger.info('Opened old html content file"')
            logger.info("oldlinks" + str(oldlinks))
    else:
        # 今回取得したリンクを記録する（上書き）
        with open(logfile_name, 'w') as f:
            f.write(str(soup))
            oldlinks = set(f)
            logger.info("oldlinks" + str(oldlinks))
except:
    # 何かしら失敗した場合はLINEに通知、ログ
    bot.send('ファイルの取得に失敗しました')
    logger.error(traceback.format_exc())
    logger.error('Failed to get csv file')

try:
    # 今回取得したリンクを記録する（上書き）
    with open(logfile_name, 'w') as f:
        f.write(str(soup))
    with open(logfile_name, 'r') as newf:
        newlinks = set(newf)
    logger.info("newlinks" + str(newlinks))
    logger.info('Writed raw html text file')
except:
    # 失敗したら通知、ログ
    bot.send('ファイルの書き込みに失敗しました')
    logger.error('Failed to write csv file')
    logger.error(traceback.format_exc())
    sys.exit(1)

try:
    # newlinks = set(links)
    # setで引き算をすると差分がわかる
    # 今回新しく発見したリンク
    added = newlinks - oldlinks
    logger.info("差分" + str(added))
    logger.info(str(len(added)))
    # 差分が１つ以上あったらLINEに通知する
    if len(added) > 0:
        bot.send("在庫表に更新がありました")
        bot.send("差分" + str(added))
    # 前回あったけど今回はなくなったリンク
    # removed = oldlinks - newlinks
    # for link in added:
    #     # 追加されたら通知
    #     # 追加されたURL自体もお知らせしようとしたらリンクをむやみに貼るなと書いてあったので一応やめておいた
    #     bot.send('リンクが追加されました')

    # for link in removed:
    #     # 追加と同様に
    #     bot.send('リンクが消去されました')

    logger.info('Compared links')

except:
    # 失敗したら…（以下略）
    bot.send('比較に失敗しました')
    logger.error('Failed to compare')
    logger.error(traceback.format_exc())
    sys.exit(1)

logger.info('DONE')
