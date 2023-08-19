import httpx

from common import HEADERS, ENV, BASE_URL, DebugTimer, print_resp


def main():
    resp = httpx.get(f'{BASE_URL}/api/books',headers=HEADERS)
    print_resp(resp=resp)

    timer = DebugTimer()

    for i, book in enumerate(resp.json()["rows"]):
        if i > 5:
            break
        media_get(book=book)

    timer.rap(message="終了")


def media_get(book):
    resp = httpx.get(f'{BASE_URL}/media/books/{book["uuid"]}',headers=HEADERS)
    print_resp(resp=resp)

    for page in range(book["page"]):
        if page > 5:
            break
        resp = httpx.get(f'{BASE_URL}/media/books/{book["uuid"]}/{str(page)}',headers=HEADERS)
        print_resp(resp=resp)
