# coding=utf-8
'''
使用父级模块名作为根模块配置 logger ，其他模块使用 __name__ 即属于子模块。
'''

import logging

def getParentPath(s):
    '''从名字中截取父模块的名字。比如输入a.b得到a'''
    for i in range(len(s) - 1, -1, -1):
        if s[i] =='.':
            break
    return s[:i]

# 初始化日志设置，以上一级作为根模块
rootPath = getParentPath(__name__)
# 基础
logger = logging.getLogger(rootPath)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# debug
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

def getRoot():
    '''应用内的根'''
    return logger

def getLogger(*args, **kw):
    return logging.getLogger(*args, **kw)

def setDebug(debug):
    logger.setLevel(logging.DEBUG if debug else logging.WARN)

logger.info('logging inited')
