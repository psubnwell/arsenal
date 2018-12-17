import json
import time
import argparse
import requests
import http.cookiejar
from retry import retry
from bs4 import BeautifulSoup
from pymongo import MongoClient

def get_info_by_id(id):
    headers = {
        'Referer': 'https://m.weibo.cn/detail/{}'.format(id),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://m.weibo.cn/api/statuses/extend'
    params = {
        'id': id
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    # 以下为发布微博的基本信息
    info = {}
    info['attitudes_count'] = data['attitudes_count']  # 点赞数
    info['comments_count'] = data['comments_count']  # 评论数
    info['created_at'] = data['created_at']
    info['reposts_count'] = data['reposts_count']  # 转发数
    info['status_title'] = data['status_title']
    info['text'] = data['text']
    # 以下为发布者的信息
    info['user'] = {}
    info['user']['follow_count'] = data['user']['follow_count']
    info['user']['followers_count'] = data['user']['followers_count']
    info['user']['gender'] = data['user']['gender']
    info['user']['id'] = data['user']['id']
    info['user']['screen_name'] = data['user']['screen_name']
    info['user']['statuses_count'] = data['user']['statuses_count']
    return info

@retry(tries=5, delay=2)
def get_reposts_per_page(id, page, cookies):
    headers = {
        'Referer': 'https://m.weibo.cn/detail/{}'.format(id),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://m.weibo.cn/api/statuses/repostTimeline'
    params = {
        'id': id,
        'page': page
    }
    response = requests.get(url, params=params, cookies=cookies, headers=headers)
    reposts = []
    for data in response.json()['data']['data']:
        # 以下为转发微博的基本信息
        repost = {}
        repost['attitudes_count'] = data['attitudes_count']
        repost['comments_count'] = data['comments_count']
        repost['created_at'] = data['created_at']
        repost['id'] = data['id']
        repost['raw_text'] = data['raw_text']
        repost['reposts_count'] = data['reposts_count']
        # 以下为转发者的基本信息
        repost['user'] = {}
        repost['user']['follow_count'] = data['user']['follow_count']
        repost['user']['followers_count'] = data['user']['followers_count']
        repost['user']['gender'] = data['user']['gender']
        repost['user']['id'] = data['user']['id']
        repost['user']['screen_name'] = data['user']['screen_name']
        repost['user']['statuses_count'] = data['user']['statuses_count']
        # 保存
        reposts.append(repost)
    return reposts

def get_reposts(id, cookies):
    # 设置 MongoDB 数据库
    client = MongoClient()
    db = client['weibo_reposts']
    collection = db[str(id)]
    # 获取总转发数
    info = get_info_by_id(id)
    reposts_count = info['reposts_count']
    print('共有 {} 条转发'.format(reposts_count))
    # 开始爬取
    num = 0  # 当前爬取的条数
    page = 1  # 当前爬取的页数
    reposts = get_reposts_per_page(id, page, cookies)
    # 如果满足下列情形之一就停止爬虫
    # 1）确认全部爬完
    # 2）爬虫经过多次尝试仍旧返回空结果
    while num < reposts_count and reposts != []:
        # 存入数据库
        collection.insert_many(reposts)
        num += len(reposts)
        if num % 5000 == 0:
            print('已经爬取 {} 条转发'.format(num))
        page += 1
        # retry 库可以自动在受阻时多次尝试
        try:
            reposts = get_reposts_per_page(id, page, cookies)
            # time.sleep(0.2)
        except:
            reposts = []
    print(num, reposts_count)


def load_cookies(cookies_file):
    cookies = http.cookiejar.LWPCookieJar()
    cookies.load(cookies_file)
    return cookies


if __name__ == '__main__':
    # info = get_info_by_id(4313825890573521)
    # print(info)
    # print(get_info_by_id(4314874903291284))
    
    # get_reposts(4314874903291284, cookies) # 希特勒
    # get_reposts(4313825890573521, cookies) # 抢方向盘
    # get_reposts(4286639154869552, cookies) # 杭州保姆
    # get_reposts(4301856895288175, cookies)  # 重庆公交

    cookies = load_cookies('./cookies')
    t1 = time.time()
    get_reposts(4313825890573521, cookies) # 抢方向盘
    t2 = time.time()
    print(t2 - t1, ' s')

