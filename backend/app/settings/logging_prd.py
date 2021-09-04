#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ログのライブラリ
import logging
from logging import getLogger, StreamHandler, Formatter, FileHandler
from datetime import datetime
import os
"""
ログファイルを作成する関数
logger_name: loggerオブジェクト名。実行ディレクトリと同じ階層にログ保存ディレクトリを作成する。

return logger: 任意のloggerオブジェクト
"""
def logging_setting(logger_name):
    """
    1. loggerの設定
    """
    # loggerオブジェクトの宣言
    logger = getLogger(str(logger_name))
    # set logging Level
    logger.setLevel(logging.DEBUG)

    """
    2. handlerの設定
    """

    # create handler
    stream_handler = StreamHandler()
    # set logging format
    handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(handler_format)

    # オブジェクト名をディレクトリ名とし、実行ディレクトリと同じ階層にログファイル保存ディレクトリを作成
    if os.path.exists(str(logger_name)) is not True:
        os.mkdir(str(logger_name))
    # テキスト出力先
    timestamp = datetime.now().strftime("%Y-%m-%d")
    # 保存する
    logging_file = '{0}/{1}_{2}.log'.format(str(logger_name), str(logger_name), timestamp)
    file_handler = FileHandler('{}'.format(logging_file))
    # set logging format for log files
    file_handler.setFormatter(handler_format)

    """
    3. loggerにhandlerをセット
    """
    # 標準出力のhandlerをセット
    logger.addHandler(stream_handler)
    # テキスト出力のhandlerをセット
    logger.addHandler(file_handler)

    return logger

if __name__ == "__main__":
    """
    ログ出力テスト
    """
    logger = logging_setting('log_test')
    logger.debug('test')
