import httpx
from common import BASE_URL, HEADERS, print_resp


def api_auth_validate():
    resp = httpx.get(f'{BASE_URL}/api/auth/validate',headers=HEADERS)
    print_resp(resp=resp)


def load_library():
    req_data = {
        "state": "load"
    }
    resp = httpx.patch(f'{BASE_URL}/media/library', json=req_data, headers=HEADERS)
    print_resp(resp=resp)
