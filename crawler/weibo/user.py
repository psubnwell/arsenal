import json
import logging
from urllib.parse import quote

import requests
import tenacity

# 设置日志
logger = logging.getLogger(__name__)

# 设置重试参数
retry_params = {
    # 当抛出异常、或者结果为None时重试
    'retry': (tenacity.retry_if_exception_type() |
              tenacity.retry_if_result(lambda result: result == None)),
    # 最多重试5次
    'stop': tenacity.stop_after_attempt(5),
    # 每次重试间隔在0-2s
    'wait': tenacity.wait_random(min=0, max=2),
    # 每次重试之前打印异常日志
    'before_sleep': tenacity.before_sleep_log(logger, logging.WARNING),
    # 如果最后一次重试仍不成功，抛出最后一次重试的异常
    'reraise': True,
}

# 设置常量
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'


@tenacity.retry(**retry_params)
def get_uid(screen_name, cookies=None):
    headers = {
        'Referer': 'https://m.weibo.cn/search?containerid={}'.format(
            quote('100103type=1&q={}'.format(screen_name))
        ),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
    }
    url = 'https://m.weibo.cn/api/container/getIndex'
    params = {
        'containerid': '100103type=3&q={}&t=0'.format(screen_name),
        'page_type': 'searchall',
    }
    response = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        timeout=5
    )
    if response.status_code != 200:
        return
    data = response.json()
    # 返回用户名搜索匹配列表
    for card in data['data']['cards']:
        if card['card_type'] == 11:
            card_group = card['card_group']
    # 返回完全匹配的用户名的UID
    for card in card_group:
        if card['card_type'] == 10 and \
           card['user']['screen_name'] == screen_name:
            return card['user']['id']

@tenacity.retry(**retry_params)
def get_info(uid, cookies=None):
    headers = {
        'Referer': 'https://m.weibo.cn/u/{}'.format(uid),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
    }
    url = 'https://m.weibo.cn/api/container/getIndex'
    params = {
        'type': 'uid',
        'value': uid,
        'containerid': str(100505) + str(uid),
    }
    response = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        timeout=5
    )
    if response.status_code != 200:
        return
    data = response.json()
    data = data['data']['userInfo']
    info = {}
    info['id'] = data['id']
    info['screen_name'] = data['screen_name']
    info['gender'] = data['gender']
    info['follow_count'] = data['follow_count']
    info['followers_count'] = data['followers_count']
    info['statuses_count'] = data['statuses_count']
    info['verified'] = data['verified']
    return info

@tenacity.retry(**retry_params)
def get_location(uid):
    headers = {
        'Referer': 'https://m.Web.cn/u/{}'.format(uid),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
    }
    url = 'https://m.weibo.cn/api/container/getIndex'
    params = {
        'type': 'uid',
        'value': str(uid),
        'containerid': '230283' + str(uid)
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return
    data = response.json()
    # 返回带有所在地的card列表
    for card in data['data']['cards']:
        if card['card_type'] == 11:
            card_group = card['card_group']
    # 返回带有所在地的card（card_type为41）
    for card in card_group:
        if card['card_type'] == 41 and \
           card['item_name'] == '所在地':
            return card['item_content']

def get_statues(uid):
    pass

def get_follows(uid):
    pass

def get_followers(uid):
    pass


if __name__ == '__main__':
    print(get_uid('胡东瑶'))
    print(get_info(3788642533))
    print(get_location(3788642533))
    # print(r.call(get_location, 3788642533))
