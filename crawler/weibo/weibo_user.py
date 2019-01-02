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

from . import util
from . import config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置其他常量
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'

@util.retry(logger=logger)
def get_user_id(screen_name, cookies=None):
    """根据用户的显示名称获取用户的ID
    """
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

@util.retry(logger=logger)
def get_info(user_id, cookies=None):
    """获取用户的基本信息

    Notes:
        分析网址: https://m.weibo.cn/u/2830678474
    """
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
    user_info = data['data']['userInfo']
    info = {}
    for key in config.USER_KEYS:
        if key == 'user_id':
            info[key] = user_info.get('id')
        elif key == 'location':
            # 地址需要在详细资料内获取
            info[key] = get_more_info(user_id, cookies).get('location')
        else:
            info[key] = user_info.get(key)
    return info

@util.retry(logger=logger)
def get_more_info(user_id, cookies=None):
    """获取用户的更多个人信息

    Notes:
        分析网址: https://m.weibo.cn/p/index?containerid=2302832830678474_-_INFO
        但目前似乎只能提取所在地
    """
    # 构造请求
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'MWeibo-Pwa': '1',
        'Referer': 'https://m.weibo.cn/p/index?containerid=230283{}_-_INFO'.format(user_id),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
    }
    url = 'https://m.weibo.cn/api/container/getIndex'
    params = {
        'containerid': str(230283) + str(user_id) + '_-_INFO',
    }
    response = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        timeout=5,
    )
    if response.status_code != 200:
        return
    # 提取数据
    data = response.json()
    more_info = {}
    for card in data['data']['cards']:
        if card['card_group'][0]['desc'] == '个人信息':
            card_group = card['card_group']
    for card in card_group:
        if card.get('item_name') == '生日':
            # 生日有若干种形式:
            # 1996-02-26 双鱼座、02-26 双鱼座、双鱼座等
            more_info['birth_date'] = card['item_content']
        if card.get('item_name') == '所在地':
            more_info['location'] = card['item_content']
        if card.get('item_name') == '大学':
            more_info['university'] = card['item_content']
        if card.get('item_name') == '公司':
            more_info['company'] = card['item_content']
    return more_info

@util.retry(logger=logger)
def get_statuses_by_page(user_id, page, cookies=None):
    """获取用户发布的微博(单页)

    Notes:
        分析网址:
    """
    # 构造请求
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
    # 提取数据
    data = response.json()
    cards = data['data']['cards']
    statuses = []
    for card in cards:
        # 跳过不是微博内容的card
        if card['card_type'] != 9:
            continue
        mblog = card['mblog']
        status = {}
        for key in config.STATUS_KEYS:
            if key == 'status_id':
                status[key] = mblog.get('id')
            elif key == 'status_bid':
                status[key] = mblog.get('bid')
            elif key == 'user':
                pass
            else:
                status[key] = mblog.get(key)
        statuses.append(status)
    return statuses

def get_statuses(user_id, count='all', cookies=None):
    """获取用户发布的微博
    """
    # 获取基本信息
    info = get_info(user_id, cookies)
    screen_name = info['screen_name']
    statuses_count = info['statuses_count']
    logger.info(
        '目标用户 %d(@%s) 共有 %d 条微博',
        user_id, screen_name, statuses_count
    )
    # 逐页获取所有转发信息
    statuses = util.get_all_pages(
        get_by_page_func=get_statuses_by_page,
        user_id=user_id,
        cookies=cookies,
        count=statuses_count if count == 'all' else count,
        logger=logger,
    )
    return statuses

@util.retry(logger=logger)
def get_follows_by_page(user_id, page, cookies=None):
    pass

def get_follows(user_id, count='all', cookies=None):
    pass

@util.retry(logger=logger)
def get_followers_by_page(user_id, page, cookies=None):
    """获取用户的粉丝列表(单页)

    Notes:
        该URL是通过一些网址片段自己摸索出来的,
        先是对用户首页(https://m.weibo.cn/profile/2830678474)的AJAX进行分析
        发现了
            fans: "/p/second?containerid=1005052830678474_-_FANS"
            follow: "/p/second?containerid=1005052830678474_-_FOLLOWERS"
            more: "/p/2304132830678474_-_WEIBO_SECOND_PROFILE_WEIBO"
        将这些地址拼接到"https://m.weibo.cn"后形成URL,
        即是用户的粉丝列表，关注列表，微博列表.

        注意! 通过直接点击用户首页上的"关注"和"粉丝"得到的页面是分组的不好处理
    """
    # 构造请求
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'MWeibo-Pwa': '1',
        'Referer': 'https://m.weibo.cn/p/second?containerid=100505{}_-_FANS'.format(user_id),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://m.weibo.cn/api/container/getSecond'
    params = {
        'containerid': str(100505) + str(user_id) + '_-_FANS',
        'page': page,
    }
    response = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        timeout=5,
    )
    if response.status_code != 200:
        return
    # 提取数据
    followers = []
    for card in response.json()['data']['cards']:
        if card['card_type'] == 10:
            follower = {}
            for key in config.USER_KEYS:
                if key == 'user_id':
                    follower[key] = int(card['user'].get('id'))
                elif key == 'location':
                    follower[key] = get_more_info(follower['user_id']).get('location')
                else:
                    follower[key] = card['user'].get(key)
            followers.append(follower)
    return followers

def get_followers(user_id, count='all', cookies=None):
    """获取用户的粉丝列表
    """
    # 获取基本信息
    info = get_info(user_id, cookies)
    screen_name = info['screen_name']
    followers_count = info['followers_count']
    logger.info(
        '目标用户 %d(@%s) 共有 %d 个粉丝',
        user_id, screen_name, followers_count
    )
    # 逐页获取所有粉丝
    followers = util.get_all_pages(
        get_by_page_func=get_followers_by_page,
        user_id=user_id,
        cookies=cookies,
        count=followers_count if count == 'all' else count,
        logger=logger
    )
    return followers

if __name__ == '__main__':
    with open('weibo/output/cookies', 'r') as f:
        cookies = json.loads(f.read())

    # 测试get_user_id
    # user_id = get_user_id('胡东瑶')
    user_id = get_user_id('崔庆才丨静觅', cookies)
    print(user_id)

    # 测试get_info
    # info = get_info(user_id, cookies)
    # print(info)

    # 测试get_more_info
    # more_info = get_more_info(user_id, cookies)
    # print(more_info)

    # 测试get_statuses_by_page
    # statuses_by_page = get_statuses_by_page(user_id, 2, cookies)
    # for i in statuses_by_page:
    #     print()
    #     print(i)

    # 测试get_statuses
    # statuses = get_statuses(user_id, cookies)
    # print(len(statuses))
    # for i in statuses[:10]:
    #     print()
    #     print(i)

    # 测试get_followers
    followers = get_followers(user_id, cookies, count=30)
    for i in followers[:10]:
        print()
        print(i)
