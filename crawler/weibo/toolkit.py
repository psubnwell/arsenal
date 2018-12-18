import argparse
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, unquote

def get_uid_by_screen_name(screen_name):
    headers = {
        'Referer': 'https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D%E5%88%98%E4%BA%A6%E8%8F%B2',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    base_url = 'https://m.weibo.cn/api/container/getIndex?'
    params = {
        'containerid': '100103type=3&q={}&t=0'.format(screen_name),
        'page_type': 'searchall',
    }
    url = base_url + urlencode(params)

    try:
        response = requests.get(url, headers=headers)
    except requests.ConnectionError as e:
        print('Error', e.args)

    if response.status_code == 200:
        data = response.json()
        # 返回用户名搜索匹配列表
        for card in data.get('data').get('cards'):
            if card.get('card_type') == 11:
                cards = card.get('card_group')
        # 返回完全匹配的用户名的UID
        for card in cards:
            if card.get('card_type') == 10 and \
               card.get('user').get('screen_name') == screen_name:
                return card.get('user').get('id')

def get_info_by_uid(uid):
    headers = {
        'Referer': 'https://m.weibo.cn/u/{}'.format(uid),
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    base_url = 'https://m.weibo.cn/api/container/getIndex?'
    params = {
        'type': 'uid',
        'value': uid,
        'containerid': str(100505) + str(uid)
    }
    url = base_url + urlencode(params)

    try:
        response = requests.get(url, headers=headers)
    except requests.ConnectionError as e:
        print('Error', e.args)

    if response.status_code == 200:
        data = response.json()
        data = data.get('data').get('userInfo')
        info = {}
        info['id'] = data.get('id')
        info['screen_name'] = data.get('screen_name')
        info['gender'] = data.get('gender')
        info['follow_count'] = data.get('follow_count')
        info['followers_count'] = data.get('followers_count')
        info['statuses_count'] = data.get('statuses_count')
        info['verified'] = data.get('verified')

    return info

def get_location_by_uid(uid):
    headers = {
        'Referer': 'https://m.Web.cn/u/{}'.format(uid),
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    base_url = 'https://m.weibo.cn/api/container/getIndex?'
    params = {
        'type': 'uid',
        'value': str(uid),
        'containerid': '230283' + str(uid)
    }
    url = base_url + urlencode(params)

    try:
        response = requests.get(url, headers=headers)
    except requests.ConnectionError as e:
        print('Error', e.args)

    if response.status_code == 200:
        data = response.json()
        # 返回带有所在地的card列表
        for card in data.get('data').get('cards'):
            if card.get('card_type') == 11:
                cards = card.get('card_group')
        # 返回带有所在地的card（card_type为41）
        for card in cards:
            if card.get('card_type') == 41 and \
               card.get('item_name') == '所在地':
                return card.get('item_content')

def get_status_by_uid(uid, count=None):
    headers = {
        'Referer': 'https://m.Web.cn/u/{}'.format(uid),
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
        # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    base_url = 'https://m.weibo.cn/api/container/getIndex?'
    params = {
        'type': 'uid',
        'value': str(uid),
        'containerid': '107603' + str(uid)
    }
    url = base_url + urlencode(params)

    statuses = []

    # if count == None:
    #     count = get_info_by_uid(uid).get('statuses_count')
    # max_page = count // 10 + 1
    for page in range(1, 3):
        params = {
            'type': 'uid',
            'value': str(uid),
            'containerid': '107603' + str(uid),
            'page': page
        }
        url = base_url + urlencode(params)

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                with open('result.json', 'a') as f:
                    f.write(json.dumps(data, indent=2, ensure_ascii=False))
                # for card in data.get('data').get('cards'):
        except requests.ConnectionError as e:
            print('Error', e.args)

        # if response.status_code == 200:
        #     data = response.json()
        #     # 返回带有所在地的card列表
        #     for card in data.get('data').get('cards'):
        #         if card.get('card_type') == 11:
        #             cards = card.get('card_group')
        #     # 返回带有所在地的card（card_type为41）
        #     for card in cards:
        #         if card.get('card_type') == 41 and \
        #            card.get('item_name') == '所在地':
        #             return card.get('item_content')




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--screen-name', type=str)
    args = parser.parse_args()

    # uid = get_uid_by_screen_name(args.screen_name)
    # info = get_info_by_uid(uid)
    # print(info)
    # localtion = get_location_by_uid(3788642533)
    # print(localtion)
    get_status_by_uid(3788642533)
