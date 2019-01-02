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

from . import util
from . import config
from . import weibo_user

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置其他常量
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'

@util.retry(logger=logger)
def get_info(status_id, cookies=None):
    """获取微博的基本信息
    """
    # 构造请求
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
    # 提取数据
    data = re.findall(r'var \$render_data = \[([\s\S]*)\]\[0\]', response.text)[0]
    data = json.loads(data)['status']
    # 提取微博的信息
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
    # 提取发布者的信息
    user = {}
    for key in config.USER_KEYS:
        if key == 'user_id':
            user[key] = int(data['user'].get('id'))
        elif key == 'location':
            user[key] = weibo_user.get_more_info(user['user_id']).get('location')
        else:
            user[key] = data['user'].get(key)
    info['user'] = user
    return info

@util.retry(logger=logger)
def get_reposts_by_page(status_id, page, cookies):
    """获取微博的转发信息(单页)
    """
    # 构造请求
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
        timeout=5,
    )
    if response.status_code != 200:
        return
    # 提取数据
    reposts = []
    for data in response.json()['data']['data']:
        # 提取转发的信息
        repost = {}
        for key in config.STATUS_KEYS:  # 转发微博和微博字段一致
            if key == 'status_id':
                repost[key] = int(data.get('id'))
            elif key == 'status_bid':
                repost[key] = data.get('bid')
            elif key == 'user':
                pass
            else:
                repost[key] = data.get(key)
        # 提取转发者的信息
        user = {}
        for key in config.USER_KEYS:
            if key == 'user_id':
                user[key] = int(data['user'].get('id'))
            elif key == 'location':
                user[key] = weibo_user.get_more_info(user['user_id']).get('location')
            else:
                user[key] = data['user'].get(key)
        repost['user'] = user
        reposts.append(repost)
    return reposts

def get_reposts(status_id, count='all', cookies=None):
    """获取微博的所有转发信息
    """
    # 获取基本信息
    info = get_info(status_id, cookies)
    reposts_count = info['reposts_count']
    logger.info('目标微博 %s 共有 %d 条转发', status_id, reposts_count)
    # 逐页获取所有转发信息
    reposts = util.get_all_pages(
        get_by_page_func=get_reposts_by_page,
        status_id=status_id,
        cookies=cookies,
        count=reposts_count if count == 'all' else count,
        logger=logger,
    )
    return reposts

@util.retry(logger=logger)
def get_comments_by_max_id(status_id, max_id=None, cookies=None):
    # 构造请求
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'MWeibo-Pwa': '1',
        'Referer': 'https://m.weibo.cn/detail/{}'.format(status_id),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://m.weibo.cn/comments/hotflow'
    params = {
        'id': status_id,
        'mid': status_id,
        'max_id': max_id,
        'max_id_type': 0,
    }
    if max_id is None:
        params.pop('max_id')
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
    comments = []
    max_id = response.json()['data']['max_id']
    data = response.json()['data']['data']
    print(data)
    print(max_id)
    for item in data:
        comment = {}
        for key in config.COMMENT_KEYS:
            if key == 'comment_id':
                comment[key] = int(item.get('id'))
            elif key == 'comment_bid':
                comment[key] = item.get('bid')
            elif key == 'user':
                pass
            else:
                comment[key] = item.get(key)
        user = {}
        for key in config.USER_KEYS:
            if key == 'user_id':
                user[key] = int(item['user'].get('id'))
            elif key == 'location':
                pass
                # user[key] = weibo_user.get_more_info(user['user_id']).get('location')
            else:
                user[key] = item['user'].get(key)
        comment['user'] = user
        comments.append(comment)
    return comments, max_id

def get_comments(status_id, count='all', cookies=None):
    # 获取基本信息
    info = get_info(status_id, cookies)
    comments_count = info['comments_count']
    logger.info('目标微博 %s 共有 %d 条评论', status_id, comments_count)
    # 准备爬取
    count = comments_count if count == 'all' else count
    num = 0
    comments = []
    ratio = 0.1
    # 爬取首页
    comments_by_max_id, max_id = get_comments_by_max_id(
        status_id=status_id,
        max_id=None,
        cookies=cookies
    )
    while num < count and max_id != 0 and comments_by_max_id is not None:
        comments += comments_by_max_id
        num += len(comments_by_max_id)
        if num / count >= ratio:
            logger.info(
                '当前 max_id = %d, 已经爬取 %d 条数据, 占设定总量的 %d%%',
                max_id, num, num / count * 100
            )
            ratio += 0.1
        # 依次爬取
        comments_by_max_id, max_id = get_comments_by_max_id(
            status_id=status_id,
            max_id=max_id,
            cookies=cookies
        )
    logger.info(
        '最终 max_id = %d, 最终爬取 %d 条数据, 占设定总量的 %d%%',
        max_id, num, num / count * 100
    )
    return comments



if __name__ == '__main__':
    import os
    output_dir = os.path.join(os.path.dirname(__file__), 'output')

    with open(os.path.join(output_dir, 'cookies'), 'r') as f:
        cookies = json.loads(f.read())

    # status_id = 4272004045840806  # 小测试用例
    status_id = 4324060840216841  # 谢娜
    # status_id = 4301856895288175  # 重庆公交

    reposts = get_reposts(status_id, cookies=cookies)
    for i in reposts[:5]:
        print(i)
    print(len(reposts))

    # # print(get_info(status_id))


    # 测试get_comments_by_max_id
    # comments, max_id = get_comments_by_max_id(status_id, max_id='245760019103155', cookies=cookies)
    # # comments, max_id = get_comments_by_max_id(status_id, cookies=cookies)
    # for i in comments:
    #     print()
    #     print(i)
    # print(max_id)


    # 测试get_comments
    # comments = get_comments(status_id, cookies=cookies)
    # for i in comments[:10]:
    #     print()
    #     print(i)
