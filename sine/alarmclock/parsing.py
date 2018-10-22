# coding=utf-8
'''
输入字符串的读取/识别方法。
以判定为前提，比如认为接下来出现的是一个时间，进行尝试转换，失败则抛出自定义异常。
每次对字符串转化，成功后返回转化后的内容，以及剩余的未转化的字符串。
'''

import datetime
from exception import ParseException, NoStringException
from globalData import data, timeFormats, dateFormats

def _tryReplace(ref, s, formats):
    '''
    从 formats 中选择首个合适的格式，把字符串 s 转化为 datetime ，再把指定字段替换到 ref 中，返回替换的结果。
    formats 为2元元组的数组。元组第一个为要格式化的字符串，第二个为字段数组，比如:
    (   '%M'   ,        ['minute', 'second', 'microsecond'])
    '''
    target = None
    for fm in formats:
        try:
            target = datetime.datetime.strptime(s, fm[0])
        except Exception, e:
            continue
        break
    if not target:
        return None
    d = {}
    for field in fm[1]:
        d[field] = target.__getattribute__(field)
    return ref.replace(**d)

zero = datetime.datetime.min.replace(year=1900) # 用于计算时长类数据
def parseString(s):
    '''读取一个字符串。以 split 默认方式分隔，即空格或者分隔符等。
    @throws NoStringException'''
    s = s.strip()
    if len(s) == 0:
        raise NoStringException()
    s = s.split(None, 1)
    return s[0], (s[1] if len(s) > 1 else '')
def parseTime(s, reference):
    '''读取一个时间（时分秒），替换到 reference 中并返回。
    @throws ParseException'''
    s = s.strip()
    if len(s) == 0:
        raise ParseException(u'缺少时间。')
    s = s.split(None, 1)
    target = _tryReplace(reference, s[0], timeFormats)
    if not target:
        raise ParseException(u'无法识别为时间:', s[0])
    return target, (s[1] if len(s) > 1 else '')
def parseDateAndTime(s, reference):
    '''读取 '日期 时间' ，日期可以没有。
    先尝试读取时间（时分秒），失败再尝试读取为 '日期 时间'
    @throws ParseException'''
    s = s.strip()
    if len(s) == 0:
        raise NoStringException()
    try:
        target, s = parseTime(s, reference)
    except ParseException as e:
        s = s.split(None, 1)
        if len(s) < 2:
            raise ParseException(u'无法识别为时间:', s[0])
        target = _tryReplace(reference, s[0], dateFormats)
        if not target:
            raise ParseException(u'无法识别为时间或日期:', s[0])
        target, s = parseTime(s[1], target)
    return target, s
def parseDateTime(s, now):
    '''读取 '日期 时间' ，日期可以没有。
    另外前缀 '-' 识别为倒计时模式，对读取到的结果从现在开始往后计算时间，比如读取到 2:00:00 则往后2小时。
    @throws ParseException'''
    s = s.strip()
    if s.startswith('-'):
        target, remain = parseDateAndTime(s[1:], zero)
        return target - zero + now, remain
    else:
        return parseDateAndTime(s, now)
def parseInt(s, default=None):
    '''读取一个整数。无字符串时返回 default ，无 default 值时抛出异常。
    @throws ParseException'''
    s = s.strip()
    if len(s) == 0:
        if default == None:
            raise NoStringException()
        else:
            return default, ''
    s = s.split(None, 1)
    try:
        index = int(s[0])
    except ValueError as e:
        raise ParseException(u'无法识别为整数:', s[0])
    return index, (s[1] if len(s) > 1 else '')
def parseAllToIndex(s):
    '''读取整个字符串为若干个整数
    @throws ParseException'''
    s = s.split()
    indexs = []
    try:
        for i in s:
            indexs.append(int(i))
    except ValueError as e:
        raise ParseException(u'无法识别为整数:', i)
    return indexs

__all__ = ['zero', 'parseString', 'parseTime', 'parseDateAndTime', 'parseDateTime', 'parseInt', 'parseAllToIndex']
