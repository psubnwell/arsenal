import json
import logging

import requests

from . import db

logger = logging.getLogger(__name__)

class ValidTester(object):
    """检测器父类

    Attributes:
        website: 站点名称
        cookies_db: Cookies数据库
        accounts_db: 账号数据库
    """
    def __init__(self, website):
        self.website = website
        self.cookies_db = db.RedisClient('cookies', self.website)
        self.accounts_db = db.RedisClient('accounts', self.website)

    def test(self, username, cookies):
        """测试方法, 需在子类中实现
        """
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
        """覆盖父类的测试方法
        """
        logger.info('正在测试用户[%s]的Cookies...', username)
        # 检测Cookies格式是否正确
        try:
            cookies = json.loads(cookies)
        except TypeError:
            logger.warning('用户[%s]的Cookies格式不合法', username)
            self.cookies_db.delete(username)
            logger.warning('用户[%s]的Cookies已删除', username)
            return
        # 检测Cookies是否有效
        try:
            test_url = 'https://m.weibo.cn'
            response = requests.get(
                url=test_url,
                cookies=cookies,
                timeout=5,
                allow_redirects=False
            )
            if response.status_code == 200:
                logger.info('用户[%s]的Cookies有效', username)
            else:
                logger.warning('用户[%s]的Cookies已失效', username)
                logger.debug('status_code: %s', response.status_code)
                logger.debug('headers: \n%s', response.headers)
                self.cookies_db.delete(username)
                logger.warning('用户[%s]的Cookies已删除', username)
        except ConnectionError:
            logger.error('发生异常', exc_info=True)

if __name__ == '__main__':
    WeiboValidTester().run()
