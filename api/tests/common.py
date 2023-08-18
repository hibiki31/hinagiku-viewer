import httpx
import json
from pprint import pprint
import time
import datetime
import sys


ENV = json.load(open('./tests/env.json', 'r'))
BASE_URL = ENV["base_url"]


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
        safe_url = str(resp.url).replace("http://", "").replace("https://", "").replace(":", "_").replace("/", "_")
        file_path = f"./tests/dump/{resp.request.method.lower()}_{safe_url}.json"
        json.dump(resp.json(), open(file_path, "w"), ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
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

# 初期化が必要であれば行う
if not httpx.get(f'{BASE_URL}/api/version').json()["initialized"]:
    req_data = {
        "username": str(ENV["username"]),
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