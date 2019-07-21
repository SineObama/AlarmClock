# coding=utf-8
'''
初始化异常时进行特定输出和程序暂停，这里只提供调用接口、保存状态。
'''

from . import mylogging
import sys
import os

logger = mylogging.getLogger(__name__)

_warning = False # 显示警告，等待回车继续（清屏）

def warn(msg, exc=None):
    '''输出信息，记录异常，并标记警告'''
    global _warning
    sys.stdout.write(msg)
    if exc:
        for arg in exc.args:
            sys.stdout.write(' ')
            sys.stdout.write(str(arg))
    sys.stdout.write('\n')
    logger.warn(msg, exc_info=(exc!=None))
    _warning = True

def reset():
    _warning = False

def warning_pause():
    '''有警告时暂停，等待回车'''
    if _warning:
        os.system('pause')

def doNothing(*args, **kwargs):
    '''用于赋值给不支持的操作'''
    pass
