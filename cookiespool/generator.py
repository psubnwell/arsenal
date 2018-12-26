import json
import logging

from . import db
from . import login

logger = logging.getLogger(__name__)

class CookiesGenerator(object):
    def __init__(self, website):
        """
        :param website: 站点名称
        """
        self.website = website
        self.accounts_db = db.RedisClient('accounts', self.website)
        self.cookies_db = db.RedisClient('cookies', self.website)

    def new_cookies(self, username, password):
        """新生成Cookies，子类需要重写

        Args:
            username: 用户名
            password: 密码
        """
        raise NotImplementedError

    def run(self):
        """运行生成模块，得到所有账户，然后顺次模拟登录
        """
        accounts_usernames = self.accounts_db.usernames()
        cookies_usernames = self.cookies_db.usernames()

        for username in accounts_usernames:
            if not username in cookies_usernames:
                password = self.accounts_db.get(username)
                logger.info('正在生成用户[%s]的Cookies...', username)
                result = self.new_cookies(username, password)
                # 获取成功
                if result.get('status') == 1:  # TODO
                    cookies = self.process_cookies(result.get('content'))
                    logger.info('用户[%s]的Cookies获取成功', username)
                    if self.cookies_db.set(username, json.dumps(cookies)):
                        logger.info('用户[%s]的Cookies保存成功')
                # 获取失败
                elif result.get('status') == 2:
                    logger.debug(result.get(content))
                    if self.accounts_db.delete(username):
                        logger.info('用户[%s]的账号已删除')  # 万一只是输错密码了呢？
                else:
                    logger.debug(result.get('content'))
        else:
            logger.info('所有账号都已经成功获取Cookies')


class WeiboCookiesGenerator(CookiesGenerator):
    def __init__(self, website='weibo'):
        """初始化微博Cookies生成器

        Args:
            website: 站点名称
        """
        CookiesGenerator.__init__(self, website)
        self.website = website

    def new_cookies(self, username, password):
        """登录微博并生成Cookies

        Args:
            username: 用户名
            password: 密码
        """
        return login.WeiboLogin(username, password)
