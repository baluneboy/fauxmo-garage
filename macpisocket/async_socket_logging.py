#!/usr/bin/env python


from pims.files.log import my_logger

def demo():
    logger = my_logger('one')
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
    
    logger = my_logger('two')
    logger.debug('debug message2')
    logger.info('info message2')
    logger.warn('warn message2')
    logger.error('error message2')
    logger.critical('critical message2')
    


if __name__ == '__main__':
    demo()
