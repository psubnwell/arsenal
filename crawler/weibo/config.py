"""
本模块用于存储配置变量.
This module stores all configuration variables.

This module is used under Chinese environment so comments are in Chinese only.
"""

import tenacity
import logging

logger = logging.getLogger(__name__)

# 设置重试参数
RETRY_PARAMS = {
    # 当抛出异常、或者结果为None时重试
    'retry': (tenacity.retry_if_exception_type() |
              tenacity.retry_if_result(lambda result: result in [None, [], False])),
    # 最多重试3次
    'stop': tenacity.stop_after_attempt(3),
    # 每次重试间隔在0-2s
    'wait': tenacity.wait_random(min=0, max=2),
    # 每次重试之前打印异常日志
    'before_sleep': tenacity.before_sleep_log(logger, logging.DEBUG),
    # 如果最后一次重试仍不成功, 默认返回None
    'retry_error_callback': lambda retry_state: None,
}

# 设置微博关键字段
STATUS_KEYS = [
    'status_id',  # 微博的ID (id = idstr = mid)
    'status_bid',  # 微博的base62编码ID
    'created_at',  # 微博的发布时间
    'raw_text',  # 微博的纯文本类型原文 (不一定存在)
    'text',  # 微博的HTML类型原文
    'reposts_count',  # 微博的转发数
    'comments_count',  # 微博的评论数
    'attitudes_count',  # 微博的点赞数
    'source',  # 微博的发布设备
    'user',  # 微博的发布者信息 (为嵌套字典)
]

# 设置用户关键字段
USER_KEYS = [
    'user_id',  # 用户的ID
    'screen_name',  # 用户的显示名称
    'gender',  # 用户性别
    'location',  # 用户地址
    'statuses_count',  # 用户发布的微博数
    'follow_count',  # 用户的关注数
    'followers_count',  # 用户的被关注数
    'urank',  # 用户等级
    'mbrank',  # 会员等级
    'mbtype',  # 会员类型
    'verified',  # 是否认证
    'verified_type',  # 认证类型
]
