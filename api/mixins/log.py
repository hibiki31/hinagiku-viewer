import logging
from pathlib import Path

from settings import DATA_ROOT, DEBUG_LOG


def setup_logger(name, logfile=f'{DATA_ROOT}/app_data/api.log'):
    Path(logfile).parent.mkdir(parents=True, exist_ok=True)
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
    if DEBUG_LOG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    return logger
