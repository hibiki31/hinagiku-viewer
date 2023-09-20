import os, uuid, datetime, shutil, glob, json, time
from PIL import Image
import imagehash


def main():
    # get_json()

    compainer_json()

    


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
            



def get_json():
    send_books_list = glob.glob(f"/opt/product_thum/*")

    start_time = time.time()

    result=[]

    for i, send_book in enumerate(send_books_list):
        ahash = imagehash.average_hash(Image.open(send_book), hash_size=16)
        whash = imagehash.whash(Image.open(send_book))         
        phash = imagehash.phash(Image.open(send_book))         
        print(i, send_book, ahash, whash)
        result.append({
            "path": send_book,
            "whash": str(whash),
            "ahash": str(ahash),
            "phash": str(phash)
        })

        if i >= 1000:
            break

    f = open("output.json", "w")
    json.dump({"result": result}, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))


if __name__ == "__main__":
    main()