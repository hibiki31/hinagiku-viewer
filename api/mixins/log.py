import logging
import os
from mixins.settings import DATA_ROOT


def setup_logger(name, logfile=f'{DATA_ROOT}app_data/api.log'):
    os.makedirs(f"{DATA_ROOT}app_data/", exist_ok=True)
    logger = logging.getLogger(name)

    # ファイル出力設定
    fh = logging.FileHandler(logfile)
    fh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(name)s - %(funcName)s - %(message)s')
    fh.setFormatter(fh_formatter)
    # ファイル出力のログレベル
    fh.setLevel(logging.DEBUG)

    # コンソール出力設定
    ch = logging.StreamHandler()
    ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(ch_formatter)
    # コンソール出力のログレベル
    ch.setLevel(logging.DEBUG)

    logger.addHandler(fh)
    logger.addHandler(ch)

    # 全体のログレベル
    logger.setLevel(logging.DEBUG)

    return logger