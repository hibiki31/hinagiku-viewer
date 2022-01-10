from asyncio import futures
import requests
import asyncio
import aiohttp

import time

API_PATH = ''
PASSWORD = ''
USER_NAME = ''


def calc_time(fn):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = fn(*args, **kwargs)
        end = time.time()
        print(f"[{fn.__name__}] elapsed time: {end - start}")
        return res
    return wrapper


@calc_time
def main():
    api_token = get_token()
    books = api_get(api_toekn=api_token)

    urls = []
    titles = []

    for book in books['rows']:
        for i in range(book['page']):
            urls.append(f'{API_PATH}/media/books/{book["uuid"]}/{i}')
        titles.append(book['title'])
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop(urls=urls))

    print(titles)

    print(f'{len(urls)} request done')


async def main_loop(urls):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for n in urls:
            tasks.append(get_request(session, n))
        await asyncio.gather(*tasks)


async def get_request(session, url):
    start = time.time()
    response = await session.get(url)
    html = await response.read()
    end = time.time()
    print(f"{str(end - start)[:6]}s {response.status} {url} - {response.headers['content-type']}", )


@calc_time
def api_get(api_toekn):
    res = requests.get(
            url=f'{API_PATH}/api/books',
            headers={'Authorization': api_toekn},
            params={"rate": 5, "libraryId": 1}
        )
    return res.json()


@calc_time
def get_token():
    res = requests.post(url=f'{API_PATH}/api/auth',data={
        'username': USER_NAME,
        'password': PASSWORD'
    })
    return "Bearer " + res.json()['access_token']


if __name__ == '__main__':
    main()