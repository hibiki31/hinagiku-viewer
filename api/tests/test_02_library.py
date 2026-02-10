import httpx
from common import BASE_URL, HEADERS, print_resp


def main():
    api_books()
    api_librarys()
    api_authors()


def api_books():
    resp = httpx.get(f'{BASE_URL}/api/books',headers=HEADERS)
    print_resp(resp=resp)

def api_librarys():
    resp = httpx.get(f'{BASE_URL}/api/librarys',headers=HEADERS)
    print_resp(resp=resp)

def api_authors():
    resp = httpx.get(f'{BASE_URL}/api/authors',headers=HEADERS)
    print_resp(resp=resp)
