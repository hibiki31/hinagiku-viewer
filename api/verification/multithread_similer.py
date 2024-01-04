import datetime
import glob
import json
import os
import shutil
import sys
import threading
import time
import uuid
from multiprocessing import Array, Manager, Pipe, Process, Queue, Value

import imagehash
from flask import Flask, render_template
from PIL import Image
from sqlalchemy import or_
from sqlalchemy.orm import Session

from books.models import BookModel, DuplicationModel
from mixins.log import setup_logger
from settings import CONVERT_THREAD, DATA_ROOT


app = Flask(__name__, static_folder='/opt/product_thum/', template_folder='./templates')


@app.route('/')
def index():
    with open("./verification/output_multiprocess_duplicate.json", "r") as f:
        data = [(os.path.basename(i[0]), os.path.basename(i[1]), i[2], i[3]) for i in json.load(f)["result"]]

        return render_template('view.j2', uuids=sorted(data, key=lambda x: x[2]))


def main():
    seq_time = 0
    thread_time = 0
    process_time = 0

    set_count = 1000
    set_number = 1

    for i in range(set_number):
        # seq_time += task_run_sequential(set_count)
        # thread_time += task_run_multithread(set_count)
        process_time += task_run_multiprocess(set_count)

    
    # print(f"[sequential] {round(seq_time/set_count/set_number*1000, 3)}s/khash {round(seq_time/seq_time*100,3)}%")
    # print(f"[multithread] {round(thread_time/set_count/set_number*1000, 3)}s/khash {round(thread_time/seq_time*100,3)}%")
    # print(f"[multiprocess] {round(process_time/set_count/set_number*1000, 3)}s/khash {round(process_time/seq_time*100,3)}%")

    # compainer_json_sequential()
    compainer_json_multiprocess()
        

def base_task_get_hash(send_book):
    book_image = Image.open(send_book)
    ahash32 = imagehash.average_hash(book_image, hash_size=32)
    ahash16 = imagehash.average_hash(book_image, hash_size=16)
    ahash8 = imagehash.average_hash(book_image, hash_size=8)
    # whash = imagehash.whash(book_image, hash_size=16)   
    # phash = imagehash.phash(book_image, hash_size=16)
    # dhash = imagehash.dhash(book_image, hash_size=16)
    # chash = imagehash.crop_resistant_hash(book_image)


    res = {
        "path": send_book,
        # "whash": str(whash),
        "ahash32": str(ahash32),
        "ahash16": str(ahash16),
        "ahash8": str(ahash8),
        # "phash": str(phash),
        # "dhash": str(dhash),
        # "chash": str(chash),
    }
    # print(res)

    return res


def compainer_json_sequential():
    f = open("./verification/output_sequential.json", "r")
    result_json = json.load(f)
    start_time = time.time()

    print(f"[sequential] {len(result_json)}件でハッシュ突合を行います 配列のメモリ使用量{round(sys.getsizeof(result_json)/1024,2)} kb")

    for i in result_json["result"]:
        for j in result_json["result"]:
            if i == j:
                continue

            hash1 = int(i["ahash"],16)
            hash2 = int(j["ahash"],16)
            if 10 < bin(hash1 ^ hash2).count('1') < 50:
                print(i["path"], j["path"], bin(hash1 ^ hash2).count('1'))
    print("[sequential] タスク終了", round(time.time()-start_time, 3))


def compainer_json_multiprocess():
    fi = open("./verification/output_multiprocess.json", "r")
    fo = open("./verification/output_multiprocess_duplicate.json", "w")
    result_json = json.load(fi)["result"]
    fi.close()
    start_time = time.time()

    print(f"[multiprocess] {len(result_json)}件でハッシュ突合を行います 配列のメモリ使用量{round(sys.getsizeof(result_json)/1024,2)} kb")

    result = []

    for i in result_json:
        for j in result_json:
            if i == j:
                continue
            
            # Ahash
            hash1 = int(i["ahash32"],16)
            hash2 = int(j["ahash32"],16)
            if bin(hash1 ^ hash2).count('1') <= 100:
                print(i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "ahash32")
                result.append((i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "ahash32"))
            
            # Ahash
            hash1 = int(i["ahash16"],16)
            hash2 = int(j["ahash16"],16)
            if bin(hash1 ^ hash2).count('1') <= 40:
                print(i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "ahash16")
                result.append((i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "ahash16"))

            # Ahash
            hash1 = int(i["ahash8"],16)
            hash2 = int(j["ahash8"],16)
            if bin(hash1 ^ hash2).count('1') <= 4:
                print(i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "ahash8")
                result.append((i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "ahash8"))
            
            # # whash
            # hash1 = int(i["whash"],16)
            # hash2 = int(j["whash"],16)
            # if bin(hash1 ^ hash2).count('1') < 50:
            #     print(i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "whash")
            #     result.append((i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "whash"))
            
            # # phash
            # hash1 = int(i["phash"],16)
            # hash2 = int(j["phash"],16)
            # if bin(hash1 ^ hash2).count('1') < 50:
            #     print(i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "phash")
            #     result.append((i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "phash"))

            # # dhash
            # hash1 = int(i["dhash"],16)
            # hash2 = int(j["dhash"],16)
            # if bin(hash1 ^ hash2).count('1') < 50:
            #     print(i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "dhash")
            #     result.append((i["path"], j["path"], bin(hash1 ^ hash2).count('1'), "dhash"))
            
            # # chash
            # hash1 = imagehash.hex_to_multihash(i["chash"])
            # hash2 = imagehash.hex_to_multihash(i["chash"])
            # hamming_distance = hash1.hash_diff(hash2)
            # if hamming_distance[0] < 3:
            #     print(i["path"], j["path"], hamming_distance[0], "chash")
            #     result.append((i["path"], j["path"], hamming_distance[0], "chash"))


    
    print(f"[multiprocess] 突合終了 {len(result_json)*len(result_json)}ペア", round(time.time()-start_time, 3))
    json.dump({"result": result}, fo, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    fo.close()
    return result


def task_run_sequential(exec_value):
    send_books_list = glob.glob(f"/opt/product_thum/*")
    start_time = time.time()

    result=[]

    print("[sequential] タスク開始", round(time.time()-start_time, 3))
    
    for i, send_book in enumerate(send_books_list[0:exec_value]):
        result.append(base_task_get_hash(send_book=send_book))

    f = open("./verification/output_sequential.json", "w")
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
    
    f = open("./verification/output_multithread.json", "w")
    json.dump({"result": result}, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    f.close()
    
    print("[multithread] タスク終了", round(time.time()-start_time, 3))
    return time.time()-start_time


def task_multiprocess(result, send_books):
    result.extend([base_task_get_hash(send_book=send_book) for send_book in send_books])


def task_run_multiprocess(exec_value):
    send_books_list = glob.glob(f"/opt/product_thum/*")
    start_time = time.time()

    with Manager() as manager:

        process_list = []
        result = manager.list()

        print("[multiprocess] タスク定義", round(time.time()-start_time, 3))
        size = len(send_books_list[0:exec_value])
        for i in range(CONVERT_THREAD):
            start = int((size*i/CONVERT_THREAD))
            end = int((size*(i+1)/CONVERT_THREAD))
            print(i, start, end)


            process_list.append(
                Process(target=task_multiprocess, args=(result, send_books_list[start:end],)),
            )

        print("[multiprocess] タスク開始", round(time.time()-start_time, 3))
        for i in process_list:
            i.start()

        print("[multiprocess] タスク待ち", round(time.time()-start_time, 3))
        for i in process_list:
            i.join()        

        f = open("./verification/output_multiprocess.json", "w")
        json.dump({"result": list(result)}, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
        f.close()
        
        print("[multithread] タスク終了", round(time.time()-start_time, 3))
        return time.time()-start_time


if __name__ == "__main__":
    main()