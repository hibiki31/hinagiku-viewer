from re import U
from django.conf.urls import url
import requests
import json
import sqlite3
import time
import sys
from datetime import datetime as dt
import pprint


DB_FILE_PATH = "tools/2021-0826-1402.db"
API_URL = "http://localhost:8000"
API_TOKEN = ""


class Color():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    END = '\033[0m'
    BOLD = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE = '\033[07m'


def LogInfo(TAG, TEXT):
    print("[" + Color.CYAN + TAG + Color.END + "] " + TEXT)


def LogError(TAG, TEXT):
    print("[" + Color.RED + TAG + Color.END + "] " + TEXT)


def LogSuccess(TAG, TEXT):
    print("[" + Color.GREEN + TAG + Color.END + "] " + TEXT)


def main():
    con = sqlite3.connect(DB_FILE_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Wallet
    bd_wallet = cur.execute("select * from wallet")
    api_wallet = requests.get(f"{API_URL}/api/rest/wallets/", params={}).json()
    api_wallet_dic = {}
    for i in api_wallet:
        api_wallet_dic[i['name']] = i['pk']

    for i in bd_wallet:
        if not i['name'] in api_wallet_dic:
            code = i['code']
            if not code:
                code = i['name']
            data = {
                'name': i['name'],
                'color': i['color'],
                'amount': i['amount'],
                'code': code,
                'kind': i['kind'],
                'is_favorite': i['is_favorite'],
                'is_hide': i['is_hide'],
            }
            post_data(url='/api/rest/wallets/', data=data)
        else:
            LogInfo(TAG='SKIP', TEXT=f"存在するためパス {i['name']}")
    
    ## SubCategory old to new
    # 追加処理
    api_data = requests.get(f"{API_URL}/api/rest/wallets/", params={}).json()
    db_data = cur.execute("select * from wallet")
    api_name_to_api_pk = {}
    for i in api_data:
        api_name_to_api_pk[i['name']] = i['pk']

    wallet_old_to_new = {}
    for i in db_data:
        wallet_old_to_new[i["id"]] = api_name_to_api_pk[i['name']]

    # BigCategory
    bd_big = cur.execute("select * from category_big")
    api_big = requests.get(f"{API_URL}/api/rest/categorys/", params={}).json()
    api_big_dic = {}
    old_to_new = {}
    for i in api_big:
        print(i)
        api_big_dic[i['name']] = i['pk']

    for i in bd_big:
        code = i['code']
        if code == "":
            code = i['name']
        if not i['name'] in api_big_dic:
            data = {
                'name': i['name'],
                'color': i['color'],
                'code': code,
                'kind': 'ex',
            }
            post_data(url='/api/rest/categorys/', data=data)
        else:
            LogInfo(TAG='SKIP', TEXT=f"存在するためパス {i['name']}")

    # 追加処理
    api_big = requests.get(f"{API_URL}/api/rest/categorys/", params={}).json()
    for i in api_big:
        print(i)
        api_big_dic[i['name']] = i['pk']

    bd_big = cur.execute("select * from category_big")
    for i in bd_big:
        old_to_new[i["id"]] = api_big_dic[i['name']]

    # SubCategory
    bd_sub = cur.execute("select * from category_sub")
    api_sub = requests.get(
        f"{API_URL}/api/rest/subcategorys/", params={}).json()

    api_sub_dic = {}
    for i in api_sub:
        api_sub_dic[i['name']] = i['pk']

    for i in bd_sub:
        code = i['code']
        if code == "":
            code = i['name']
        if not i['name'] in api_sub_dic:
            data = {
                'name': i['name'],
                'code': code,
                'category': old_to_new[i['category_big_id']],
            }
            post_data(url='/api/rest/subcategorys/', data=data)
        else:
            LogInfo(TAG='SKIP', TEXT=f"存在するためパス {i['name']}")
    
    ## SubCategory old to new
    # 追加処理
    api_data = requests.get(f"{API_URL}/api/rest/subcategorys/", params={}).json()
    db_data = cur.execute("select * from category_sub")
    api_name_to_api_pk = {}
    for i in api_data:
        api_name_to_api_pk[i['name']] = i['pk']

    sub_category_old_to_new = {}
    for i in db_data:
        sub_category_old_to_new[i["id"]] = api_name_to_api_pk[i['name']]

    # Items
    items = cur.execute("""
    select item.name, item.kind, amount, sub.id as sub_id, wallet_income_id, wallet_expenses_id, shop, date
    from item 
        left join 'transaction' as tr on transaction_id = tr.id 
        left join category_sub as sub on category_sub_id = sub.id 
        left join category_big as big on sub.category_big_id = big.id 
    """)

    suppliers = get_data(url="/api/rest/suppliers", data={})

    suppliers_name_list = []

    for i in suppliers:
        suppliers_name_list.append(i['name'])

    for i in items:
        if not i["shop"].strip() in suppliers_name_list:
            post_data(url='/api/rest/suppliers/', data={'name': i["shop"].strip()})
            suppliers_name_list.append(i['shop'].strip())
    
    ## Shop name to id
    # 追加処理
    api_data = requests.get(f"{API_URL}/api/rest/suppliers/", params={}).json()
    db_data = cur.execute("select * from category_sub")
    shop_name_to_pk = {}
    for i in api_data:
        shop_name_to_pk[i['name']] = i['pk']
    
    # transaction
    items = cur.execute("""
    select item.name, item.kind, amount, sub.id as sub_id, wallet_income_id, wallet_expenses_id, shop, date
    from item 
        left join 'transaction' as tr on transaction_id = tr.id 
        left join category_sub as sub on category_sub_id = sub.id 
        left join category_big as big on sub.category_big_id = big.id 
    """)
    for i in items:
        i = dict(i)
        print(i)
        if i["kind"] == "transfer":
            amount_income = i["amount"]
            amount_expenses = i["amount"]
        elif i["kind"] == "expenses":
            amount_income = 0
            amount_expenses = i["amount"]
        elif i["kind"] == "income":
            amount_income = i["amount"]
            amount_expenses = 0
        data = {
            'date':str(i['date']),
            'kind':i['kind'],
            'items':[{
                'name': i['name'],
                'sub_category_id': sub_category_old_to_new[i['sub_id']],
                'amount_income':amount_income,
                'amount_expenses':amount_expenses
            }],
            'supplier_id': int(shop_name_to_pk[i['shop'].strip()]),
            'wallet_expenses_id':int(wallet_old_to_new[i['wallet_expenses_id']]),
            'wallet_income_id': int(wallet_old_to_new[i['wallet_income_id']])
        }
        post_data(f"/api/rest/transactions/",data=data)






def get_data(url, data):
    response = requests.get(API_URL+url, params=data)
    if response.status_code == 200:
        LogSuccess("OK", "Get succes " + url)
    else:
        LogError("ER", "Get error " + url)
    return response.json()


def post_data(url, data):
    print(data)
    response = requests.post(
        url=API_URL+url,
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    if (response.status_code == 200) or (response.status_code == 201):
        LogSuccess("OK", "Post succes " + url)
    else:
        LogError("ER", "Post error " + url)
        pprint.pprint(response.json())
        sys.exit(1)
    
    return response


if __name__ == '__main__':
    main()
