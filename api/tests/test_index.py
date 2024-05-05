import httpx

from common import HEADERS, ENV, BASE_URL, DebugTimer, print_resp
from concurrent.futures import ThreadPoolExecutor

from time import sleep, time
import csv

from datetime import datetime


class DebugTimer():
    def __init__(self):
        self.data = []
        self.time = time()
    def rap(self):
        now_time = time()
        run_time = (now_time - self.time) * 1000
        print(f'{run_time:.1f}ms')
        self.data.append(run_time)
        self.time = now_time


def main():
    # 現在の日付と時刻を取得
    now = datetime.now()

    # YYMMDDhhmmssの形式の文字列に変換
    formatted_date = now.strftime("%y%m%d%H%M%S")
    
    timer = DebugTimer()
    for i in range(0,100):
        resp = httpx.get(f'{BASE_URL}/api/books',headers=HEADERS, params={
            "limit": 60,
            "offset": 60*i,
            "libraryId": 4,
        })
        timer.rap()
        
    with open(f'request_result{formatted_date}.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(timer.data)
        
    
if __name__ == "__main__":
    main()
    
    
    
    