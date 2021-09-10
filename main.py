import os
from selenium import webdriver
from selenium_chrome.source.fake_useragent import UserAgent
import sys
import traceback
import requests
from bs4 import BeautifulSoup
from backend.app.func.notify import LINENotifyBot
from backend.app.settings.logging_prd import logging_setting
from backend.app.settings.config_file import CHECK_URL, LINE_NOTIFY_SANRES_ACCESS_TOKEN
from backend.app.func.connect_firestorage import upload_bucket_file, download_bucket_file
# import chromedriver_binary
from selenium import webdriver
import difflib

# ログの記録するフォーマットを決める
logger = logging_setting("/tmp")
# 比較用テキストファイル
logfile_name = "/tmp/sanres_log.txt"
# チェックしたいURL
url = CHECK_URL
# LINE notifyのアクセストークン
bot = LINENotifyBot(LINE_NOTIFY_SANRES_ACCESS_TOKEN)


def handler(request):
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('user-agent='+UserAgent().random)
    # chrome_options.add_argument('–user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25')

    chrome_options.binary_location = os.getcwd() + "/selenium_chrome/source/headless-chromium"
    driver = webdriver.Chrome(os.getcwd() + "/selenium_chrome/source/chromedriver",chrome_options=chrome_options)
    # 以前のデータ
    beforedata_list = []
    # 新たに取得したデータ
    nowdata_list = []
    try:
        # seleniumの準備
        # options = webdriver.ChromeOptions()
        # botで弾かれないようにユーザーエージェントを付ける
        # options.add_argument('–user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25')
        # seleniumでchromeを立ち上げる
        driver = webdriver.Chrome(options=chrome_options)
        # webページを開く
        el_class = driver.get(url)
        # カレンダーのみを取得
        el_class = driver.find_element_by_class_name("cmn_calender_col02")
        # カレンダーに書かれているテキストを取得
        nowdata = el_class.text
        # ページのソースを取得
        link_source = driver.page_source
    except:
        logger.error(traceback.format_exc())
        # 取得に失敗した場合もLINEに通知してログを取る
        bot.send('URLの取得に失敗しました')
        bot.send(traceback.format_exc())
        # 念の為強制終了
        sys.exit(1)

    try:
        # 前回取得したリンクをダウンロードする
        with open(logfile_name, 'wb') as beforef:
        # with open("tmp/before_sanres_log.txt", 'wb') as beforef:
            # ファイルをダウンロードする
            # download_bucket_file(logfile_name, "tmp/before_sanres_log.txt", logger)
            download_bucket_file(logfile_name, logfile_name, logger)
        # ダウンロードファイルがあったら読み込む
        if os.path.exists(str(logfile_name)):
            # 前回取得したリンクをファイルから読み込む
            with open(logfile_name, 'r') as f:
                logger.info("ファイル"+ str(f))
                # 前回のリンクをセット
                beforedata = str(f)
                for line1 in f:
                    beforedata_list.append(line1)
                # beforedata_list = str(f.read().splitlines())
                logger.info('Opened old html content file"')
                logger.info("oldata" + str(beforedata_list))
        # ファイルがなかったら新たに作る
        else:
            # 今回取得したリンクを記録する
            with open(logfile_name, 'w') as f:
                f.write(str(nowdata))
            upload_bucket_file(logfile_name, logfile_name, "text/plain", logger)
            with open(logfile_name, 'r') as oldf:
                beforedata = str(oldf)
                for line1 in oldf:
                    beforedata_list.append(line1)
                logger.info("olddata" + str(beforedata_list))
    except:
        # 何かしら失敗した場合はLINEに通知、ログ
        bot.send('ファイルの取得に失敗しました')
        logger.error(traceback.format_exc())
        logger.error('Failed to get text file')

    try:
        # 今回取得したリンクを記録する（上書き）
        with open(logfile_name, 'w') as f:
            f.write(str(nowdata))
        upload_bucket_file(logfile_name, logfile_name, "text/plain", logger)
        with open(logfile_name, 'r') as newf:
            newdata = str(newf)
            for line1 in newf:
                nowdata_list.append(line1)
            logger.info("nowdata" + str(nowdata_list))
        logger.info('Writed raw html text file')
    except:
        # 失敗したら通知、ログ
        bot.send('ファイルの書き込みに失敗しました')
        logger.error('Failed to write csv file')
        logger.error(traceback.format_exc())
        sys.exit(1)

    try:
        # 文字列を比較する
        result = nowdata_list.copy()
        # 今のデータのリストを１つずつ取り出す
        for value in beforedata_list:
            # 前のデータに重複したものがあったら消す
            if value in result:
                result.remove(value)
        logger.info("before file: " + str(beforedata_list))
        logger.info("new file: " + str(nowdata_list))
        logger.info("差分判定結果: {}".format(result))
        # リストに要素があったら差分を表示する
        if len(result) > 0:
            # 差分が１つ以上あったらLINEに通知する
            bot.send("在庫表に更新がありました")
            bot.send("現在のデータ\n" + str(nowdata_list))
        else:
            logger.info("差分はありません")

        logger.info('Compared links')

    except:
        # 失敗したら…（以下略）
        bot.send('比較に失敗しました')
        logger.error('Failed to compare')
        logger.error(traceback.format_exc())
        sys.exit(1)

    logger.info('DONE')


def hello_world():
    return "hello world"

# def check_sanres_update():
#     # 以前のデータ
#     beforedata_list = []
#     # 新たに取得したデータ
#     nowdata_list = []
#     try:
#         # seleniumの準備
#         options = webdriver.ChromeOptions()
#         # botで弾かれないようにユーザーエージェントを付ける
#         options.add_argument('–user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25')
#         # seleniumでchromeを立ち上げる
#         driver = webdriver.Chrome(options=options)
#         # webページを開く
#         el_class = driver.get(url)
#         # カレンダーのみを取得
#         el_class = driver.find_element_by_class_name("cmn_calender_col02")
#         # カレンダーに書かれているテキストを取得
#         nowdata = el_class.text
#         # ページのソースを取得
#         link_source = driver.page_source
#     except:
#         logger.error(traceback.format_exc())
#         # 取得に失敗した場合もLINEに通知してログを取る
#         bot.send('URLの取得に失敗しました')
#         bot.send(traceback.format_exc())
#         # 念の為強制終了
#         sys.exit(1)

#     try:
#         # 前回取得したリンクをダウンロードする
#         with open(logfile_name, 'wb') as beforef:
#         # with open("tmp/before_sanres_log.txt", 'wb') as beforef:
#             # ファイルをダウンロードする
#             # download_bucket_file(logfile_name, "tmp/before_sanres_log.txt", logger)
#             download_bucket_file(logfile_name, logfile_name, logger)
#         # ダウンロードファイルがあったら読み込む
#         if os.path.exists(str(logfile_name)):
#             # 前回取得したリンクをファイルから読み込む
#             with open(logfile_name, 'r') as f:
#                 logger.info("ファイル"+ str(f))
#                 # 前回のリンクをセット
#                 beforedata = str(f)
#                 for line1 in f:
#                     beforedata_list.append(line1)
#                 # beforedata_list = str(f.read().splitlines())
#                 logger.info('Opened old html content file"')
#                 logger.info("oldata" + str(beforedata_list))
#         # ファイルがなかったら新たに作る
#         else:
#             # 今回取得したリンクを記録する
#             with open(logfile_name, 'w') as f:
#                 f.write(str(nowdata))
#             upload_bucket_file(logfile_name, logfile_name, "text/plain", logger)
#             with open(logfile_name, 'r') as oldf:
#                 beforedata = str(oldf)
#                 for line1 in oldf:
#                     beforedata_list.append(line1)
#                 logger.info("olddata" + str(beforedata_list))
#     except:
#         # 何かしら失敗した場合はLINEに通知、ログ
#         bot.send('ファイルの取得に失敗しました')
#         logger.error(traceback.format_exc())
#         logger.error('Failed to get text file')

#     try:
#         # 今回取得したリンクを記録する（上書き）
#         with open(logfile_name, 'w') as f:
#             f.write(str(nowdata))
#         upload_bucket_file(logfile_name, logfile_name, "text/plain", logger)
#         with open(logfile_name, 'r') as newf:
#             newdata = str(newf)
#             for line1 in newf:
#                 nowdata_list.append(line1)
#             logger.info("nowdata" + str(nowdata_list))
#         logger.info('Writed raw html text file')
#     except:
#         # 失敗したら通知、ログ
#         bot.send('ファイルの書き込みに失敗しました')
#         logger.error('Failed to write csv file')
#         logger.error(traceback.format_exc())
#         sys.exit(1)

#     try:
#         # 文字列を比較する
#         result = nowdata_list.copy()
#         # 今のデータのリストを１つずつ取り出す
#         for value in beforedata_list:
#             # 前のデータに重複したものがあったら消す
#             if value in result:
#                 result.remove(value)
#         logger.info("before file: " + str(beforedata_list))
#         logger.info("new file: " + str(nowdata_list))
#         logger.info("差分判定結果: {}".format(result))
#         # リストに要素があったら差分を表示する
#         if len(result) > 0:
#             # 差分が１つ以上あったらLINEに通知する
#             bot.send("在庫表に更新がありました")
#             bot.send("現在のデータ\n" + str(nowdata_list))
#         else:
#             logger.info("差分はありません")

#         logger.info('Compared links')

#     except:
#         # 失敗したら…（以下略）
#         bot.send('比較に失敗しました')
#         logger.error('Failed to compare')
#         logger.error(traceback.format_exc())
#         sys.exit(1)

#     logger.info('DONE')

    # try:
    #     # HTMLを取得する
    #     # html = urllib.request.urlopen(url)
    #     html = requests.get(url, headers=headers_dic)
    #     # HTMLのステータスコード（正常に取得できたかどうか）を記録する
    #     logger.info("html content" + str(html.content))
    #     logger.info('HTTP STATUS CODE: ' + str(html.status_code))
    # except:
    #     # 取得に失敗した場合もLINEに通知してログを取る
    #     bot.send('URLの取得に失敗しました')
    #     # 念の為強制終了
    #     sys.exit(1)

    # # 取得したリクエストをパースする
    # # soup = BeautifulSoup(html.content, "html.parser")
    # soup = BeautifulSoup(link_source, "html.parser")
    # logger.info("get Beautiful soup" + str(soup))
    # # HTMLの中からaタグのみを抽出
    # # tags = soup.find_all("a")
    # links = list()
    # # 前回取ったリンク
    # oldlinks = set()
    # # 今回とったリンク
    # newlinks = set()
    # # for tag in tags:
    # #     # aタグからリンクのURLのみを取り出す。
    # #     links.append(tag.get('href'))
    # try:
    #     # 今回取得したリンクを記録する（上書き）
    #     with open(logfile_name, 'wb') as beforef:
    #         # ファイルをダウンロードする
    #         # download_bucket_file(logfile_name, logfile_name, logger)
    #         download_bucket_file(logfile_name, logfile_name, logger)
    #     if os.path.exists(str(logfile_name)):
    #         # 前回取得したリンクをファイルから読み込む
    #         with open(logfile_name, 'r') as f:
    #             logger.info("ファイル"+ str(f))
    #             # 前回のリンクにセット
    #             oldlinks = set(f)
    #             # reader = csv.reader(f)
    #             # for row in reader:
    #             #     oldlinks = set(row)
    #             logger.info('Opened old html content file"')
    #             logger.info("oldlinks" + str(oldlinks))
    #     else:
    #         # 今回取得したリンクを記録する（上書き）
    #         with open(logfile_name, 'w') as f:
    #             f.write(str(soup))
    #         upload_bucket_file(logfile_name, logfile_name, "text/plain", logger)
    #         with open(logfile_name, 'r') as oldf:
    #             oldlinks = set(oldf)
    #             logger.info("oldlinks" + str(oldlinks))
    # except:
    #     # 何かしら失敗した場合はLINEに通知、ログ
    #     bot.send('ファイルの取得に失敗しました')
    #     logger.error(traceback.format_exc())
    #     logger.error('Failed to get csv file')

    # try:
    #     # 今回取得したリンクを記録する（上書き）
    #     with open(logfile_name, 'w') as f:
    #         f.write(str(soup))
    #     upload_bucket_file(logfile_name, logfile_name, "text/plain", logger)
    #     # ファイルをダウンロードする
    #     # download_bucket_file(logfile_name, logfile_name, logger)
    #     with open(logfile_name, 'r') as newf:
    #         newlinks = set(newf)
    #     logger.info("newlinks" + str(newlinks))
    #     logger.info('Writed raw html text file')
    # except:
    #     # 失敗したら通知、ログ
    #     bot.send('ファイルの書き込みに失敗しました')
    #     logger.error('Failed to write csv file')
    #     logger.error(traceback.format_exc())
    #     sys.exit(1)

    # try:
    #     # newlinks = set(links)
    #     # setで引き算をすると差分がわかる
    #     # 今回新しく発見したリンク
    #     added = newlinks - oldlinks
    #     logger.info("差分" + str(added))
    #     logger.info(str(len(added)))
    #     # 差分が１つ以上あったらLINEに通知する
    #     if len(added) > 0:
    #         bot.send("在庫表に更新がありました")
    #         bot.send("差分" + str(added))
    #     # 前回あったけど今回はなくなったリンク
    #     # removed = oldlinks - newlinks
    #     # for link in added:
    #     #     # 追加されたら通知
    #     #     # 追加されたURL自体もお知らせしようとしたらリンクをむやみに貼るなと書いてあったので一応やめておいた
    #     #     bot.send('リンクが追加されました')

    #     # for link in removed:
    #     #     # 追加と同様に
    #     #     bot.send('リンクが消去されました')

    #     logger.info('Compared links')

    # except:
    #     # 失敗したら…（以下略）
    #     bot.send('比較に失敗しました')
    #     logger.error('Failed to compare')
    #     logger.error(traceback.format_exc())
    #     sys.exit(1)

    # logger.info('DONE')
if __name__ == '__main__':
    handler()
