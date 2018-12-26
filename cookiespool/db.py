import random

import redis

class RedisClient(object):
    """Redis数据库客户端

    Attributes:
        db: 数据库
        type: 存储数据类型（accounts、cookies等）
        website: 站点名称
    """
    def __init__(self, type, website, host, port, password):
        """初始化Redis连接

        Args:
            type: 存储数据类型（accounts、cookies等）
            website: 站点名称
            host: 地址
            port: 端口
            password: 密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        self.type = type
        self.website = website

    def name(self):
        """获取Hash的名称
        """
        return '{type}:{website}'.format(type=self.type, website=self.website)

    def set(self, username, value):
        """设置键值对

        Args:
            username: 用户名
            value: 密码或Cookies
        """
        return self.db.hset(self.name(), username, value)

    def get(self, username):
        """根据键名获取键值（密码或Cookies）

        Args:
            username: 用户名
        """
        return self.db.hget(self.name(), username)

    def delete(self, username):
        """根据键名删除键值对

        Args:
            username: 用户名
        """
        return self.db.hdel(self.name(), username)

    def count(self):
        """获取键值对的总数量
        """
        return self.db.hlen(self.name())

    def random(self):
        """随机得到键值，可用于随机Cookies获取
        """
        return random.choice(self.db.hvals(self.name))

    def usernames(self):
        """获取所有键名（用户名）
        """
        return self.db.hkeys(self.name())

    def all(self):
        """获取所有键值对
        """
        return self.db.hgetall(self.name())
