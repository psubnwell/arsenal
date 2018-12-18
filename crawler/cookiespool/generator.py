import json

import config
from cookiespool.db import RedisClient

class CookiesGenerator(object):
    def __init__(self, website):
        """
        :param website: 站点名称
        """
        self.website = website
        self.accounts_db = RedisClient('accounts', self.website)
        self.cookies_db = RedisClient('cookies', self.website)


    def run(self):
        """运行生成模块，得到所有账户，然后顺次模拟登录
        :return:
        """
        accounts_usernames = self.accounts_db.usernames()
        cookies_usernames = self.cookies_db.usernames()

        for username in accounts_usernames:
            if not username in cookies_usernames:
                password = self.accounts_db.get(username)
                result = self.new_
