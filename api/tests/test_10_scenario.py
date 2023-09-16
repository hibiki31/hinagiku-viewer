import httpx

from common import HEADERS, ENV, BASE_URL, DebugTimer, print_resp
from concurrent.futures import ThreadPoolExecutor

from time import sleep

def main():
    worker_patch()
    multi()

def multi():
    resp = httpx.get(f'{BASE_URL}/api/books',headers=HEADERS)
    print_resp(resp=resp)

    timer = DebugTimer()
    with ThreadPoolExecutor(max_workers=8) as e:
        for i, book in enumerate(resp.json()["rows"]):
            if i > 10:
                break
            e.submit(media_get, book)
    timer.rap(message="マルチスレッド終了")

    

def worker_patch():
    resp = httpx.get(f'{BASE_URL}/api/books',headers=HEADERS)
    print_resp(resp=resp)

    for i, book in enumerate(resp.json()["rows"]):
        if i > 10:
            break
        resp_patch = httpx.patch(f'{BASE_URL}/media/books',headers=HEADERS,json={
            "uuid": book["uuid"],
            "height": 1000
        })
        print_resp(resp=resp_patch)
        sleep(10)
        


def single(book):
    resp = httpx.get(f'{BASE_URL}/api/books',headers=HEADERS)
    print_resp(resp=resp)

    timer = DebugTimer()
    for i, book in enumerate(resp.json()["rows"]):
        if i > 10:
            break
        media_get(book=book)
    timer.rap(message="シングルスレッド終了")


def media_get(book):
    resp = httpx.get(f'{BASE_URL}/media/books/{book["uuid"]}',headers=HEADERS)
    print_resp(resp=resp)

    for page in range(book["page"]):
        if page > 5:
            break
        resp = httpx.get(f'{BASE_URL}/media/books/{book["uuid"]}/{str(page)}',headers=HEADERS, params={"height": 1112 })
        print_resp(resp=resp)
