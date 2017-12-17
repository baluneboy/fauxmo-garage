#!/usr/bin/env python

# FIXME make rotating handler by file size (with compression?)

import datetime
import logging

loggers = {}


def my_logger(name):
    global loggers

    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        now = datetime.datetime.now()
        handler = logging.FileHandler(
            '/Users/ken/log/%s' % name 
            + now.strftime("%Y-%m-%d") 
            + '.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        loggers.update(dict(name=logger))

        return logger


def demo():
    logger = my_logger('fauxmo_garage')
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')


if __name__ == '__main__':
    demo()
