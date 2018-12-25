import os
import logging
import logging.handlers

class TqdmLoggingHandler(logging.Handler):
    """A handler for logging module to prevent tqdm progress bar
    from getting interrupted while logging.

    To use this class, just replaces logging.StreamHandler() with
    TqdmLoggingHandler().

    Notices:
        This class can be ignored if you don't use tqdm module.
    """
    def __init__(self, level=logging.NOTSET):
        super(self.__class__, self).__init__(level)

    def emit(self, record):
        import tqdm
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def create_logger(log_dir='log'):
    """Create a logger for your application.

    References:
        [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html#)
    """
    # create logger with name
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # create log directory.
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    # create file handler which logs even debug messages
    fh = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'log'),
        maxBytes=1048576,  # 1 MB
        backupCount=1
    )
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s: (%(name)s) %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
