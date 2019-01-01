"""
本模块用于获取以用户ID为输入的相关信息.
This module can be applied to get all information given user ID.

This module is used under Chinese environment so comments are in Chinese only.
"""

import json
import logging
from urllib.parse import quote

import requests
import tenacity

from . import config

# 设置日志
logging.basicConfig(level=logging.INFO)  # 用于调试
logger = logging.getLogger(__name__)


config.RETRY_PARAMS.update({'before_sleep': tenacity.before_sleep_log(logger, logging.WARNING)})

# 设置常量
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'

@tenacity.retry(**config.RETRY_PARAMS)
def get_user_id(screen_name, cookies=None):
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
    # 返回完全匹配的用户名的USER_ID
    for card in card_group:
        if card['card_type'] == 10 and \
           card['user']['screen_name'] == screen_name:
            return card['user']['id']

@tenacity.retry(**config.RETRY_PARAMS)
def get_info(user_id, cookies=None):
    headers = {
        'Referer': 'https://m.weibo.cn/u/{}'.format(user_id),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
    }
    url = 'https://m.weibo.cn/api/container/getIndex'
    params = {
        'type': 'uid',
        'value': user_id,
        'containerid': str(100505) + str(user_id),
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
    # 设置要提取的用户信息
    keys = [
        'user_id',
        'screen_name',
        'gender',
        'location',
        'statuses_count',
        'follow_count',
        'followers_count',
        'urank',  # 用户等级
        'mbrank',  # 会员等级
        'mbtype',  # 会员类型
        'verified',  # 是否认证
        'verified_type',  # 认证类型
    ]
    user_info = data['data']['userInfo']
    info = {}
    for key in keys:
        if key == 'user_id':
            info[key] = user_info.get('id')
        elif key == 'location':
            info[key] = get_location(user_id, cookies)  # 地址需要在详细资料内获取
        else:
            info[key] = user_info.get(key)
    return info

@tenacity.retry(**config.RETRY_PARAMS)
def get_location(user_id, cookies=None):
    headers = {
        'Referer': 'https://m.weibo.cn/p/index?containerid=230283{}_-_INFO'.format(user_id),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
    }
    url = 'https://m.weibo.cn/api/container/getIndex'
    params = {
        'containerid': str(230283) + str(user_id) + '_-_INFO',
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return
    data = response.json()
    for card in data['data']['cards']:
        if card['card_group'][0]['desc'] == '个人信息':
            card_group = card['card_group']
    for card in card_group:
        if card.get('item_name') == '所在地':
            return card['item_content']

@tenacity.retry(**config.RETRY_PARAMS)
def get_statuses_per_page(user_id, page, cookies=None):
    headers = {
        'Referer': 'https://m.weibo.cn/u/{}'.format(user_id),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
    }
    url = 'https://m.weibo.cn/api/container/getIndex'
    params = {
        'type': 'uid',
        'value': str(user_id),
        'containerid': str(107603) + str(user_id),
        'page': page,
    }
    if page == 1:
        params.pop('page')
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
    # 设置要提取的微博信息
    keys = [
        'status_id',  # 微博的ID (id = idstr = mid)
        'status_bid',  # 微博的base62编码ID
        'created_at',  # 发布时间
        'raw_text', # HTML型原文
        'text', # 文本型原文
        'reposts_count',  # 转发数
        'comments_count',  # 评论数
        'attitudes_count',  # 点赞数
        'source',  # 发布设备
    ]
    cards = data['data']['cards']
    statuses = []
    for card in cards:
        # 跳过不是微博内容的card
        if card['card_type'] != 9:
            continue
        mblog = card['mblog']
        status = {}
        for key in keys:
            if key == 'status_id':
                status[key] = mblog.get('id')
            elif key == 'status_bid':
                status[key] = mblog.get('bid')
            else:
                status[key] = mblog.get(key)
        statuses.append(status)
    return statuses

def get_statuses(user_id, cookies=None):
    # 获取微博数
    info = get_info(user_id, cookies)
    screen_name = info['screen_name']
    statuses_count = info['statuses_count']
    logger.info('用户 %s(@%s) 共有 %d 条微博', user_id, screen_name, statuses_count)
    # 开始爬取
    num = 0
    page = 1
    statuses = []
    # 爬取首页
    statuses_per_page = get_statuses_per_page(user_id, page, cookies)
    while num < statuses_count and statuses_per_page:
        statuses += statuses_per_page
        num += len(statuses_per_page)
        logger.info('已经爬取 %d 页, 共 %d 条微博', page, num)
        page += 1
        # 爬取下一页
        try:
            statuses_per_page = get_statuses_per_page(user_id, page, cookies)
        except tenacity.RetryError:
            statuses_per_page = []
            logger.info('第 %d 页为空页', page)
            # 尝试往后继续爬取3页
            for i in range(1, 4):
                try:
                    statuses_per_page = get_statuses_per_page(user_id, page+i, cookies)
                except tenacity.RetryError:
                    statuses_per_page = []
                    logger.info('第 %d 页为空页', page + i)
                    continue
                if statuses_per_page:
                    page += i
                    break
    return statuses


def get_follows(user_id):
    pass

def get_followers(user_id):
    pass


if __name__ == '__main__':
    with open('weibo/output/cookies', 'r') as f:
        cookies = json.loads(f.read())

    # 测试get_user_id
    # user_id = get_user_id('胡东瑶')
    user_id = get_user_id('崔庆才丨静觅')
    print(user_id)

    # 测试get_info
    info = get_info(user_id)
    print(info)

    # 测试get_statuses_per_page
    # statuses_per_page = get_statuses_per_page(user_id, 2, cookies)
    # for i in statuses_per_page:
    #     print()
    #     print(i)

    # 测试get_statuses
    # statuses = get_statuses(user_id, cookies)
    # print(len(statuses))
    # for i in statuses[:]:
    #     print()
    #     print(i)
