import logging

import tenacity

def retry(logger):
    """重试函数
    """
    return tenacity.retry(
        # 当抛出异常、或者结果为空时重试
        retry = (tenacity.retry_if_exception_type() |
                 tenacity.retry_if_result(
                     lambda result: result in [None, [], False]
                 )),
        # 最多重试3次
        stop = tenacity.stop_after_attempt(3),
        # 每次重试间隔在0-2s
        wait = tenacity.wait_random(min=1, max=3),
        # 每次重试之前打印异常日志
        before_sleep = tenacity.before_sleep_log(logger, logging.WARNING),
        # 如果最后一次重试仍不成功, 默认返回None
        retry_error_callback = lambda retry_state: None,
    )

def get_all_pages(get_by_page_func, count, logger, ahead=3, **kw):
    """用于爬取多页数据的函数

    Args:
        get_by_page_func (func): 爬取单页数据的函数
        count (int): 设定的或者预期的数据条数
        ahead (int): 如遇空页尝试再爬几页
                     有些网站因为隐私设置等原因每页数据显示不完整, 可能有伪空页
        logger: 日志实例
        **kw: get_by_page_func()需要用到的参数
    """
    # 准备爬取
    num = 0
    page = 1
    items = []
    ratio = 0.1
    # 爬取首页
    items_by_page = get_by_page_func(page=page, **kw)
    # 如果满足下列情形之一就停止爬虫
    # 1) 确认全部爬完
    # 2) 爬虫经过多次尝试(尝试重新爬取本页、尝试往后继续爬取若干页)仍旧返回空结果
    while num < count and items_by_page is not None:
        # 保存
        items += items_by_page
        num += len(items_by_page)
        if num / count >= ratio:
            logger.info(
                '已经爬取 %d 页, 共 %d 条数据, 占设定总量的 %d%%',
                page, num, num / count * 100
            )
            ratio += 0.1
        # 爬取下一页
        page += 1
        items_by_page = get_by_page_func(page=page, **kw)
        # 如果本页为空页, 尝试往后继续爬取若干页
        if items_by_page is None and ahead != 0:
            logger.info('第 %d 页为空页, 将尝试往后爬取 %d 页', page, ahead)
            for i in range(1, ahead + 1):
                items_by_page = get_by_page_func(page=page + i, **kw)
                if items_by_page is not None:
                    logger.info('第 %d 页为非空页, 继续爬取', page + i)
                    page += i
                    break
                elif i == ahead:
                    logger.info('第 %d 页为空页, 终止爬取', page + i)
                else:
                    logger.info('第 %d 页为空页', page + i)
                    continue
    logger.info(
        '最终爬取 %d 页, 共 %d 条数据, 占设定总量的 %d%%',
        page, num, num / count * 100
    )
    return items

