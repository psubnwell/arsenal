import json
import logging

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
def get_info(id, cookies=None):
    headers = {
        'Referer': 'https://m.weibo.cn/detail/{}'.format(id),
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
    }
    url = 'https://m.weibo.cn/api/statuses/extend'
    params = {
        'id': id
    }
    response = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies
    )
    data = response.json()
    with open('data.json', 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
    # 以下为发布微博的基本信息
    info = {}
    info['created_at'] = data['created_at']
    info['text'] = data['text']
    info['reposts_count'] = data['reposts_count']  # 转发数
    info['comments_count'] = data['comments_count']  # 评论数
    info['attitudes_count'] = data['attitudes_count']  # 点赞数
    info['status_title'] = data['status_title']
    # 以下为发布者的信息
    info['user'] = {}
    info['user']['follow_count'] = data['user']['follow_count']
    info['user']['followers_count'] = data['user']['followers_count']
    info['user']['gender'] = data['user']['gender']
    info['user']['id'] = data['user']['id']
    info['user']['screen_name'] = data['user']['screen_name']
    info['user']['statuses_count'] = data['user']['statuses_count']
    return info


def get_comments(id):
    pass

def get_reposts(id):
    pass


if __name__ == '__main__':
    print(get_info(4301856895288175))  # 重庆公交
