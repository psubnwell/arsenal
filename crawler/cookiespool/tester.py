import json

import requests

from cookiespool.db import RedisClient

class ValidTester(object):
    """检测器父类
    """
    def __init__(self, website):
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)

    def test(self, username, cookies):
        # 需在子类中实现
        raise NotImplementedError

    def run(self):
        cookies_groups = self.cookies_db.all()
        for username, cookies in cookies_groups.item():
            self.test(username, cookies)

class WeiboValidTester(ValidTester):
    """微博检测器子类
    """
    def __init__(self, website='weibo'):
        ValidTester.__init__(self, website)

    def test(self, username, cookies):
        print('正在测试{}的Cookies'.format(username))
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('Cookies不合法', username)
            self.cookies_db.delete(username)
            print('删除Cookies', username)
            return
        try:
            test_url = config.TEST_URL_MAP[self.website]
            response = requests.get(test_url, cookies=cookies, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                print('Cookies有效', username)
            else:
                print(response.status_code, response.headers)
                print('Cookies失效', username)
                self.cookies_db.delete(username)
                print('删除Cookies', username)
        except ConnectionError as e:
            print('发生异常', e.args)


if __name__ == '__main__':
    WeiboValidTester().run()
