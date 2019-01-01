"""
本模块用于获取以微博ID为输入的相关信息.
This module can be applied to get all information given status ID.

This module is used under Chinese environment so comments are in Chinese only.
"""

import re
import json
import logging

import requests
import tenacity

from . import config
from . import user as weibo_user

# 设置日志
logging.basicConfig(level=logging.INFO)  # 用于调试
logger = logging.getLogger(__name__)

config.RETRY_PARAMS.update({'before_sleep': tenacity.before_sleep_log(logger, logging.WARNING)})

# 设置常量
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'

@tenacity.retry(**config.RETRY_PARAMS)
def get_info(status_id, cookies=None):
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': USER_AGENT,
    }
    url = 'https://m.weibo.cn/detail/{}'.format(status_id)
    response = requests.get(
        url,
        headers=headers,
        cookies=cookies
    )
    if response.status_code != 200:
        return
    data = re.findall(r'var \$render_data = \[([\s\S]*)\]\[0\]', response.text)[0]
    data = json.loads(data)['status']
    info = {}
    for key in config.STATUS_KEYS:
        if key == 'status_id':
            info[key] = int(data.get('id'))
        elif key == 'status_bid':
            info[key] = data.get('bid')
        elif key == 'user':
            pass
        else:
            info[key] = data.get(key)
    user = {}
    for key in config.USER_KEYS:
        if key == 'user_id':
            user[key] = int(data['user'].get('id'))
        elif key == 'location':
            user[key] = weibo_user.get_location(user['user_id'])
        else:
            user[key] = data['user'].get(key)
    info['user'] = user
    return info

@tenacity.retry(**config.RETRY_PARAMS)
def get_reposts_per_page(status_id, page, cookies):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'MWeibo-Pwa': '1',
        'Referer': 'https://m.weibo.cn/detail/{}'.format(status_id),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://m.weibo.cn/api/statuses/repostTimeline'
    params = {
        'id': status_id,
        'page': page,
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
    reposts = []
    for data in response.json()['data']['data']:
        repost = {}
        for key in config.STATUS_KEYS:  # 转发微博和微博的实质一样
            if key == 'status_id':
                repost[key] = int(data.get('id'))
            elif key == 'status_bid':
                repost[key] = data.get('bid')
            elif key == 'user':
                pass
            else:
                repost[key] = data.get(key)
        user = {}
        for key in config.USER_KEYS:
            if key == 'user_id':
                user[key] = int(data['user'].get('id'))
            elif key == 'location':
                user[key] = weibo_user.get_location(user['user_id'])
            else:
                user[key] = data['user'].get(key)
        repost['user'] = user
        reposts.append(repost)
    return reposts

def get_reposts(status_id, cookies):
    info = get_info(status_id, cookies)
    reposts_count = info['reposts_count']
    logger.info('目标微博 %s 共有 %d 条转发', status_id, reposts_count)
    # 开始爬取
    num = 0
    page = 1
    reposts = []
    # 爬取首页
    reposts_per_page = get_reposts_per_page(status_id, page, cookies)
    while num < reposts_count and reposts_per_page:
        reposts += reposts_per_page
        num += len(reposts_per_page)
        logger.info('已经爬取 %d 页, 共 %d 条转发', page, num)
        page += 1
        # 爬取下一页
        reposts_per_page = get_reposts_per_page(status_id, page, cookies)
        if reposts_per_page is None:
            logger.info('第 %d 页为空页', page)
            # 尝试往后继续爬取3页
            for i in range(1, 4):
                reposts_per_page = get_reposts_per_page(
                    status_id,
                    page + i,
                    cookies
                )
                if reposts_per_page is None:
                    logger.info('第 %d 页为空页', page + i)
                    continue
                else:
                    page += i
                    break
    return reposts

def get_comments(status_id):
    pass

if __name__ == '__main__':
    import os
    output_dir = os.path.join(os.path.dirname(__file__), 'output')

    with open(os.path.join(output_dir, 'cookies'), 'r') as f:
        cookies = json.loads(f.read())


    status_id = 4272004045840806  # 小测试用例
    # status_id = 4301856895288175  # 重庆公交
    reposts = get_reposts(status_id, cookies)
    for i in reposts[:5]:
        print(i)
    print(len(reposts))

    # # print(get_info(status_id))
