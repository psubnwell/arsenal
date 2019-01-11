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
import fake_useragent

from . import util
from . import config
from . import weibo_user

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置用户代理
ua = fake_useragent.UserAgent()


@util.retry(logger=logger)
def get_info(status_id, cookies=None):
    """获取微博的基本信息
    """
    # 构造请求
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua.random,
    }
    url = 'https://m.weibo.cn/detail/{}'.format(status_id)
    response = requests.get(
        url,
        headers=headers,
        cookies=cookies,
        timeout=5,
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
    """获取微博的转发(单页)
    """
    # 构造请求
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'MWeibo-Pwa': '1',
        'Referer': 'https://m.weibo.cn/detail/{}'.format(status_id),
        'User-Agent': ua.random,
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
    """获取微博的所有转发
    """
    # 获取基本信息
    info = get_info(status_id, cookies)
    reposts_count = info['reposts_count']
    logger.info('目标微博 %s 共有 %d 条转发', status_id, reposts_count)
    count = reposts_count if count == 'all' else count
    logger.info('设定爬取数量 %d 条', count)
    # 逐页获取所有转发信息
    reposts = util.get_all_pages(
        get_by_page_func=get_reposts_by_page,
        status_id=status_id,
        cookies=cookies,
        count=count,
        logger=logger,
    )
    return reposts

@util.retry(logger=logger)
def get_comments_by_page(status_id, page, cookies=None):
    """获取微博的评论(单页)
    """
    # 构造请求
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'MWeibo-Pwa': '1',
        'Referer': 'https://m.weibo.cn/detail/{}'.format(status_id),
        'User-Agent': ua.random,
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://m.weibo.cn/api/comments/show'
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
    comments = []
    for data in response.json()['data']['data']:
        # 提取评论的信息
        comment = {}
        for key in config.COMMENT_KEYS:
            if key == 'comment_id':
                comment[key] = int(data.get('id'))
            elif key == 'like_count':
                # 存在不同URL返回字段有差异的情况
                # 本方法用到的URL返回like_counts
                # 而get_comments_by_max_id()方法中用到的URL返回like_count
                comment[key] = data.get('like_counts')
            elif key == 'user':
                pass
            else:
                comment[key] = data.get(key)
        # 提取评论者的信息
        user = {}
        for key in config.USER_KEYS:
            if key == 'user_id':
                user[key] = int(data['user'].get('id'))
            elif key == 'location':
                user[key] = weibo_user.get_more_info(user['user_id']).get(
                    'location'
                )
            else:
                user[key] = data['user'].get(key)
        comment['user'] = user
        comments.append(comment)
    return comments

def get_comments(status_id, count='all', cookies=None):
    """获取微博的所有评论

    Notices:
        根据经验, 爬取评论时最好将爬虫频率降低一些, 并且多往后看几页.
    """
    # 获取基本信息
    info = get_info(status_id, cookies)
    comments_count = info['comments_count']
    logger.info('目标微博 %s 共有 %d 条评论', status_id, comments_count)
    count = comments_count if count == 'all' else count
    logger.info('设定爬取数量 %d 条', count)
    # 逐页获取所有评论信息
    comments = util.get_all_pages(
        get_by_page_func=get_comments_by_page,
        status_id=status_id,
        cookies=cookies,
        count=count,
        logger=logger,
    )
    return comments


"""
目前还存在异常的方法
"""

@util.retry(logger=logger)
def get_comments_by_max_id(status_id, max_id=None, cookies=None):
    """获取微博的评论(单页, 基于max_id)

    Warning:
        本方法目前只能获取单页, 原因未知.
        已经采用多种方法debug, 如使用真实登录Cookies等, 仍不成功.
        建议用get_comments_by_page()替代.
    """
    # 构造请求
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'MWeibo-Pwa': '1',
        'Referer': 'https://m.weibo.cn/detail/{}'.format(status_id),
        'User-Agent': ua.random,
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
    # print(data)
    # print(max_id)
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
                user[key] = weibo_user.get_more_info(user['user_id']).get('location')
            else:
                user[key] = item['user'].get(key)
        comment['user'] = user
        comments.append(comment)
    return comments, max_id

def get_comments_based_on_max_id(status_id, count='all', cookies=None):
    """获取微博的所有评论(基于max_id)

    Warning:
        本方法目前只能获取单页, 原因未知, 建议用get_comments_by_page()替代.
    """
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
    # cookies = None

    # status_id = 4272004045840806  # 小测试用例
    status_id = 4324060840216841  # 谢娜
    # status_id = 4301856895288175  # 重庆公交

    print(get_info(status_id))


    # reposts = get_reposts(status_id, cookies=cookies)
    # for i in reposts[:5]:
    #     print(i)
    # print(len(reposts))


    # 测试get_comments_by_max_id
    # comments, max_id = get_comments_by_max_id(status_id, max_id='245760019103155', cookies=cookies)
    # # comments, max_id = get_comments_by_max_id(status_id, cookies=cookies)
    # for i in comments:
    #     print()
    #     print(i)
    # print(max_id)


    # 测试get_comments
    comments = get_comments(status_id, count='all', cookies=cookies)
    with open(os.path.join(output_dir, 'comments.txt'), 'w') as f:
        for i in comments:
            f.write(json.dumps(i, ensure_ascii=False))
            f.write('\n')
