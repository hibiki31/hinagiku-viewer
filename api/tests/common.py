import httpx
import json
from pprint import pprint
import time
import datetime
import sys


ENV = json.load(open('./tests/env.json', 'r'))
BASE_URL = ENV["base_url"]


class DebugTimer():
    def __init__(self):
        self.time = time.time()
    def rap(self, message, level='debug'):
        now_time = time.time()
        run_time = (now_time - self.time) * 1000
        if level == 'info':
            print(f'{run_time:.1f}ms - {message}')
        else:
            print(f'{run_time:.1f}ms - {message}')
        self.time = now_time


class Color:
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'
    CYAN      = '\033[36m'
    WHITE     = '\033[37m'
    END       = '\033[0m'
    BOLD      = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE   = '\033[07m'


def print_resp(resp: httpx.Response, allow_not_found=False, debug=False):
    if resp.status_code == 200:
        print(f"{Color.BLUE}{resp} {resp.request.method} {resp.url}{Color.END}")
        dumpjson(resp)
    else:
        print(f"{Color.RED}{resp} {resp.request.method} {resp.url}{Color.END}")

    if debug:
        print("-------------------------------------")
        pprint(resp.json()) 
        print("-------------------------------------")
        print()

    if allow_not_found and resp.status_code == 404:
        print(f"{Color.GREEN}Allow not found{Color.END}")
    elif resp.status_code != 200:
        print(resp.json())
        raise Exception

def dumpjson(resp: httpx.Response):
    safe_url = str(resp.url).replace("http://", "").replace("https://", "").replace(":", "_").replace("/", "_")
    file_path = f"./tests/dump/{resp.request.method.lower()}_{safe_url}"
    content_type = resp.headers["content-type"]
    if content_type == "application/json":
        json.dump(resp.json(), open(f"{file_path}.json", "w"), ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))

# 初期化が必要であれば行う
if not httpx.get(f'{BASE_URL}/api/version').json()["initialized"]:
    req_data = {
        "id": str(ENV["username"]),
        "password": str(ENV["password"])
    }
    resp = httpx.post(f'{BASE_URL}/api/auth/setup', json=req_data)
    print_resp(resp=resp)


# トークンの取得
req_data = {
    "username": ENV["username"],
    "password": ENV["password"]
}
resp = httpx.post(f'{BASE_URL}/api/auth', data=req_data)
print_resp(resp=resp)

# トークンを変数に格納
ACCESS_TOKEN = resp.json()["access_token"]
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'    
}