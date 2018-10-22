# coding=utf-8
'''日期时间 datetime 相关的接口、变量、辅助函数'''

import datetime

everyday = '1234567'
day = datetime.timedelta(1)

def getNow(): # 用于在可能的测试中控制时间
    return datetime.datetime.now()

def formatWeekdays(weekdays):
    '''对星期进行格式化: 得到7个字符，分别为数字1-7，开启时为数字，关闭时对应位置为空格'''
    if weekdays == None:
        weekdays = ''
    d = {}
    for i in everyday:
        d[i] = False
    for i in weekdays:
        d[i] = True
    weekdays = ''
    for i in everyday:
        weekdays += i if d[i] else ' '
    return weekdays

def getNextFromWeekday(now, time, weekdays='', forceToday=False):
    '''为星期重复闹钟确定下一次时间。
    now 为现在， time 为原本或期望的下次闹钟时间。
    保证最终的时间比现在晚，如果 time 已经比现在晚则根据 forceToday 有2种情况: 
    设置 forceToday 则强制从今天重新计算（取 time 的时分秒）；否则从 time 往后计算。'''
    if now > time or forceToday:
        time = resetToday(now, time)
        if now > time:
            time += day
    weekdays = formatWeekdays(weekdays)
    if weekdays.isspace():
        weekdays = everyday
    while str(time.weekday()+1) not in weekdays:
        time += day
    return time

def resetToday(now, time):
    '''返回 now 的日期和 time 的时分秒。'''
    return now.replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=time.microsecond)

def getNextAfterNow(now, time):
    '''如果时间比现在早，则推迟天数直到比现在晚。'''
    if now > time:
        time = resetToday(now, time)
        if now > time:
            time += day
    return time
