import time
import logging
from multiprocessing import Process

from . import api
from . import generator
from . import tester

logger = logging.getLogger(__name__)

class Scheduler(object):
    @staticmethod
    def valid_cookies(cycle):
        while True:
            logger.info('Cookies检测进程开始运行')

    @staticmethod
    def generate_cookies()
