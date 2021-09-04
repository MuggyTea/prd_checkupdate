import os
import time

try:
    from ..settings.firebase import bucket
except:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    from settings.firebase import bucket


def upload_bucket_file(source_filename, upload_filename, content_type, logger):
    logger.info('File {0} uploaded to {1}'.format(source_filename, upload_filename))
    try:
        # firestorageにアップロードするファイル名・場所を指定
        blob = bucket.blob(upload_filename)
        # ローカルに一度落としたアップロードファイルを指定
        blob.upload_from_filename(source_filename, content_type)
        # アクセスできるようにする
        blob.make_public()
        # URL取得
        file_URL = blob.public_url
        logger.info("uploaded success: URL: {0} blob: {1}, filename: {2} ".format(file_URL, blob, upload_filename))
        return file_URL
    except:
        for i in range(3 + 1):
            logger.error('{0} upload retry {1}'.format(source_filename, i))
            sleep_sec = 3
            logger.error('sleep {} sec'.format(sleep_sec))
            time.sleep(sleep_sec)
            # firestorageにアップロードするファイル名
            blob = bucket.blob(upload_filename)
            # アップロードするファイルを指定
            blob.upload_from_filename(source_filename, content_type)
            if blob:
                logger.info("uploaded success")
                # URL取得
                file_URL = blob.public_url
                logger.info("uploaded success: URL: {0} blob: {1}, filename: {2} ".format(file_URL, blob, upload_filename))
                return file_URL
        logger.info("uploaded failed")
        # URL取得
        file_URL = ''
        logger.info("uploaded faild: URL: {0} blob: {1}, filename: {2} ".format(file_URL, blob, upload_filename))
        return file_URL


def download_bucket_file(source_filename, download_filename, logger):
    # どこにダウンロードするか
    blob = bucket.blob(source_filename)
    try:
        logger.info(
            'Blob {0} downloaded to {1}'.format(source_filename, download_filename))
        # firestorageにあるダウンロードしたいファイル名を指定
        blob.download_to_filename(download_filename)
    except:  # firebaseにファイルが存在しない場合（初めてのユーザー）
        logger.info('{} does not exist'.format(download_filename))
        if os.path.exists(source_filename):
            # ローカルのディレクトリを削除する
            os.remove(source_filename)
        return


if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    from settings.logging import logging_setting
    logger = logging_setting('TweetGeneratorModelTextLogging')
    filename = "get_tweets_assets/aquirax_k/tweets_3200_raw_aquirax_k.pkl"
    upload_bucket_file(filename, logger)
