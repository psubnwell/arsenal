"""
本模块用于转换微博移动端和网页端的网址.
This module can be applied to convert URL between mobile and web.

This module is used under Chinese environment so comments are in Chinese only.
"""

from . import weibo_status
from . import base62


def mobile2web(mobile_url, type):
    """将微博移动端网址转化为网页端网址
    """
    # 如果网址有参数, 就移除
    if '?' in mobile_url:
        mobile_url = mobile_url.split('?')[0]
    # 如果网址末尾有'/', 就移除
    if mobile_url.endswith('/'):
        mobile_url = mobile_url[:-1]
    # 判断类型, 进行转换
    if type == 'status':
        status_id = mobile_url.split('/')[-1]
        info = weibo_status.get_info(status_id)
        user_id = info['user']['id']
        status_bid = info['bid']
        return 'https://weibo.com/{}/{}'.format(user_id, status_bid)
    elif type == 'user':
        pass  # TODO

def web2mobile(web_url, type):
    """将微博网页端网址转化为移动端网址
    """
    # 如果网址有参数, 就移除
    if '?' in web_url:
        web_url = web_url.split('?')[0]
    # 如果网址末尾有'/', 就移除
    if web_url.endswith('/'):
        web_url = web_url[:-1]
    # 判断类型, 进行转换
    if type == 'status':
        status_bid = web_url.split('/')[-1]
        status_id = base62.bid2id(status_bid)
        return 'https://m.weibo.cn/detail/{}'.format(status_id)
    elif type == 'user':
        pass  # TODO


if __name__ == '__main__':
    mobile_url = 'https://m.weibo.cn/detail/4301856895288175'
    web_url = 'https://weibo.com/1618051664/H0MiZmbH9'
    assert mobile2web(mobile_url, type='status') == web_url
    assert web2mobile(web_url, type='status') == mobile_url
