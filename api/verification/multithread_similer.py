import datetime
import glob
import json
import os
import shutil
import time
import uuid

import imagehash
from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy import or_

from books.models import BookModel, DuplicationModel
from mixins.log import setup_logger
from settings import DATA_ROOT, CONVERT_THREAD
import threading
from multiprocessing import Process, Queue, Value, Array, Pipe


def main():
    seq_time = 0
    thread_time = 0
    process_time = 0

    set_count = 100
    set_number = 3

    for i in range(set_number):
        seq_time += task_run_sequential(set_count)
        thread_time += task_run_multithread(set_count)
        process_time += task_run_multiprocess(set_count)

    
    print(f"[sequential] {round(seq_time/set_count/set_number*1000, 3)}s/khash {round(seq_time/seq_time*100,3)}%")
    print(f"[multithread] {round(thread_time/set_count/set_number*1000, 3)}s/khash {round(thread_time/seq_time*100,3)}%")
    print(f"[multiprocess] {round(process_time/set_count/set_number*1000, 3)}s/khash {round(process_time/seq_time*100,3)}%")
        

def base_task_get_hash(send_book):
    book_image = Image.open(send_book)
    ahash = imagehash.average_hash(book_image, hash_size=16)
    whash = imagehash.whash(book_image)         
    phash = imagehash.phash(book_image)  

    res = {
        "path": send_book,
        "whash": str(whash),
        "ahash": str(ahash),
        "phash": str(phash)
    }
    # print(res)

    return res


def compainer_json():
    f = open("output.json", "r")
    result_json = json.load(f)
    for i in result_json["result"]:
        for j in result_json["result"]:
            if i == j:
                continue

            hash1 = int(i["ahash"],16)
            hash2 = int(j["ahash"],16)
            if 10 < bin(hash1 ^ hash2).count('1') < 50:
                print(i["path"], j["path"], bin(hash1 ^ hash2).count('1'))
            

def task_run_sequential(exec_value):
    send_books_list = glob.glob(f"/opt/product_thum/*")
    start_time = time.time()

    result=[]

    print("[sequential] タスク開始", round(time.time()-start_time, 3))
    
    for i, send_book in enumerate(send_books_list[0:exec_value]):
        result.append(base_task_get_hash(send_book=send_book))

    f = open("output_sequential.json", "w")
    json.dump({"result": result}, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    f.close()
    
    print("[sequential] タスク終了", round(time.time()-start_time, 3))
    return time.time()-start_time


def task_multithread(send_book, result):
    result.append(base_task_get_hash(send_book=send_book))


def task_run_multithread(exec_value):
    send_books_list = glob.glob(f"/opt/product_thum/*")
    start_time = time.time()

    result=[]
    thread = []

    print("[multithread] タスク定義", round(time.time()-start_time, 3))
    for i, send_book in enumerate(send_books_list[0:exec_value]):
        thread.append(threading.Thread(target=task_multithread, args=(send_book, result, )))
    
    print("[multithread] タスク開始 ", round(time.time()-start_time, 3))
    for i in thread:
        i.start()
    
    print("[multithread] タスク待ち", round(time.time()-start_time, 3))
    for i in thread:
        i.join()
    
    f = open("output_multithread.json", "w")
    json.dump({"result": result}, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    f.close()
    
    print("[multithread] タスク終了", round(time.time()-start_time, 3))
    return time.time()-start_time


def task_multiprocess(send_rev, send_books):
    send_rev.send([base_task_get_hash(send_book=send_book) for send_book in send_books])


def task_run_multiprocess(exec_value):
    send_books_list = glob.glob(f"/opt/product_thum/*")
    start_time = time.time()

    process_list = []
    result = []

    print("[multiprocess] タスク定義", round(time.time()-start_time, 3))
    size = len(send_books_list[0:exec_value])
    for i in range(CONVERT_THREAD):
        start = int((size*i/CONVERT_THREAD))
        end = int((size*(i+1)/CONVERT_THREAD))
        print(i, start, end)

        get_rev,send_rev  = Pipe(False)
        process_list.append((
            Process(target=task_multiprocess, args=(send_rev, send_books_list[start:end],)),
            get_rev
        ))

    print("[multiprocess] タスク開始", round(time.time()-start_time, 3))
    for i in process_list:
        i[0].start()

    print("[multiprocess] タスク待ち", round(time.time()-start_time, 3))
    for i in process_list:
        i[0].join()
        result.extend(i[1].recv())
    

    f = open("output_multiprocess.json", "w")
    json.dump({"result": result}, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    f.close()
    
    print("[multithread] タスク終了", round(time.time()-start_time, 3))
    return time.time()-start_time



if __name__ == "__main__":
    main()