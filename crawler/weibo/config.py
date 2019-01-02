"""
本模块用于存储配置变量.
This module stores all configuration variables.

This module is used under Chinese environment so comments are in Chinese only.
"""

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
    # 'location',  # 用户地址 (这一项不是基本信息, 需花额外时间获取)
    'statuses_count',  # 用户发布的微博数
    'follow_count',  # 用户的关注数
    'followers_count',  # 用户的被关注数
    'urank',  # 用户等级
    'mbrank',  # 会员等级
    'mbtype',  # 会员类型
    'verified',  # 是否认证
    'verified_type',  # 认证类型
]

# 设置评论关键字段
COMMENT_KEYS = [
    'comment_id',  # 评论的ID
    'comment_bid',  # 评论的base62编码ID
    'created_at',  # 评论的发布时间
    'text',  # 评论原文
    'like_count',  # 评论的点赞数
    'user',  # 评论的发布者信息 (为嵌套字典)
]
