import asyncio

import requests


async def get_url(url):
    result = requests.get(url)
    return result.status_code

async def main(urls):
    tasks = [asyncio.create_task(get_url(url)) for url in urls]
    return await asyncio.gather(*tasks)

if __name__ == '__main__':
    urls = [
        "http://www.baidu.com",
        "http://www.taobao.com",
        "http://www.jd.com"
    ]
    result = asyncio.run(main(urls))
    print(result)
