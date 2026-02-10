import json
import sys
import time

import imagehash


def main():
    compainer_json_sequential_bin()
    compainer_json_sequential_hash()



def compainer_json_sequential_bin():
    f = open("./verification/output_sequential.json")
    result_json = json.load(f)
    start_time = time.time()

    print(f"[sequential] {len(result_json['result'])}件でハッシュ突合を行います 配列のメモリ使用量{round(sys.getsizeof(result_json)/1024,2)} kb")

    for i in result_json["result"]:
        for j in result_json["result"]:
            if i == j:
                continue

            hash1 = int(i["ahash"],16)
            hash2 = int(j["ahash"],16)
            score = bin(hash1 ^ hash2).count('1')
            if score  < 10:
                print(i["path"], j["path"], score)
    print("[sequential-bin] タスク終了", round(time.time()-start_time, 5))


def compainer_json_sequential_hash():
    f = open("./verification/output_sequential.json")
    result_json = json.load(f)
    start_time = time.time()

    print(f"[sequential] {len(result_json)}件でハッシュ突合を行います 配列のメモリ使用量{round(sys.getsizeof(result_json)/1024,2)} kb")

    for i in result_json["result"]:
        for j in result_json["result"]:
            if i == j:
                continue

            hash1 = imagehash.hex_to_hash(i["ahash"])
            hash2 = imagehash.hex_to_hash(j["ahash"])
            score = hash1 - hash2
            if score < 10:
                print(i["path"], j["path"], score)
    print("[sequential-hash] タスク終了", round(time.time()-start_time, 5))


if __name__ == "__main__":
    main()
