# coding=utf-8
'''自定义异常。
初衷是区分于系统异常，判断为自身逻辑或用户操作不当。'''

import sys

class ClientException(Exception):
    '''基类:客户端异常（虽然没有服务器？）。基本上都是用户操作不当'''
    def __str__(self):
        '''用于不小心 print 时的自动转换，目标编码为 stdout 指定'''
        args = []
        for i in self.args:
            if isinstance(i, unicode):
                args.append(i.encode(sys.stdout.encoding))
            else:
                args.append(i)
        return ' '.join(args)
    def __unicode__(self):
        args = []
        for i in self.args:
            if isinstance(i, str):
                args.append(i.decode(sys.stdout.encoding))
            else:
                args.append(i)
        return ' '.join(args)
    def printMsg(self):
        for i in self.args:
            sys.stdout.write(str(i))
            sys.stdout.write(' ')
        sys.stdout.write('\n')
class ClockException(ClientException):
    '''与闹钟相关的异常'''
    pass
class ParseException(ClientException):
    '''转换异常。发生在从输入命令读取内容时'''
    pass
class NoStringException(ParseException):
    '''缺少字符串'''
    def __init__(self):
        super(NoStringException, self).__init__(u'缺少指令参数。')
