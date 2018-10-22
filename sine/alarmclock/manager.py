# coding=utf-8
'''闹钟管理/服务接口'''

import threading
from plone.synchronize import synchronized
from mydatetime import *
from exception import ClockException
from entity import *
from globalData import clocks, data, config

_data_filepath = config['datafile']
_sort = lambda x:(x['time'] if x['on'] else datetime.datetime.max)
_clock_lock = threading.RLock()

@synchronized(_clock_lock)
def _init():
    import sys
    import os
    import shutil
    from sine.path import Path
    from initUtil import warn
    from player import isLegal
    # 读取数据文件，忽略文件不存在的情况，读取异常时对原文件进行备份
    try:
        fail = False
        with open(_data_filepath, 'a+') as file:
            for line in file:
                try:
                    clocks.append(eval(line))
                except Exception as e:
                    warn(u'读取一行闹钟数据失败: %s。' % (line), e)
                    fail = True
        if fail:
            location = Path(_data_filepath).join('..').join('clocks_packup')
            tail = 0
            while (os.path.isfile(location + str(tail))):
                tail += 1
            shutil.copyfile(_data_filepath, location + str(tail))
    except Exception, e:
        warn(u'打开闹钟数据文件 %s 失败。' % (_data_filepath), e)
        raw_input('press enter to exit')
        sys.exit(1)
    refreshWeekly()
    resortAndSave()

    # 检查音频文件是否存在
    for clock in clocks:
        if not isLegal(clock['sound']):
            warn(u'闹钟[%s]的音频\'%s\'无效。' % (clock, clock['sound']))
    if not isLegal(config['default_sound']):
        warn(u'默认铃声设置\'default_sound\'无效，将会使用beep音。', e)
        config['default_sound'] = 'default'

def getReminds():
    '''检查是否有需要提醒的闹钟，并返回。主要的状态检查接口。'''
    reminds = []
    now = getNow()
    for clock in clocks:
        if clock.checkRemind(now):
            reminds.append(clock)
    return reminds

def getExpired():
    expired = []
    for clock in clocks:
        if clock.isExpired():
            expired.append(clock)
    return expired

@synchronized(_clock_lock)
def add(clock):
    clocks.append(clock)
    return

@synchronized(_clock_lock)
def get(index, defaultFirst=False):
    '''参数从1开始（数组从0开始），检查越界（允许0代表默认操作，defaultFirst返回第一个闹钟否则None）'''
    if index > len(clocks) or index < 0:
        raise ClockException(u'序号 %d 超出范围。' % (index))
    if index > 0:
        return clocks[index - 1]
    if not defaultFirst:
        return None
    if len(clocks) == 0:
        raise ClockException(u'当前无闹钟。')
    return clocks[0]

@synchronized(_clock_lock)
def cancel(clock):
    '''取消闹钟
    传入None为默认操作: 关掉第一个提醒或到期闹钟
    对一次性闹钟: 删除
    对星期重复: 取消下一个提醒
    对周期重复: 以当前时间重新开始计时
    对关闭的闹钟无效'''
    now = getNow()
    
    # choose clock
    if clock == None: # choose first expired
        clock = _getFirstRemindOrExpired(clocks, now)
        if not clock:
            raise ClockException(u'没有可取消的闹钟。')
    
    if not clock['on']:
        raise ClockException(u'此闹钟已关闭，无法取消。')
    
    # cancel it
    clock.cancel()
    if isinstance(clock, OnceClock):
        clocks.remove(clock)
    return

@synchronized(_clock_lock)
def switch(indexs):
    '''变换开关。
    传入空列表执行默认操作: 改变第一个提醒或到期闹钟，或者第一个闹钟。
    会重置提醒时间。
    会删除一次性闹钟。
    对星期重复: 开启时以当前时间为准，重置为下一个闹钟时间；
    对周期重复: 开启时如果过期，则以当前时间重新开始计时。
    无视越界'''
    now = getNow()
    if len(clocks) == 0:
        return
    
    # choose clock(s)
    chooseds = []
    if len(indexs) == 0:
        found = _getFirstRemindOrExpired(clocks, now)
        chooseds = [found if found else clocks[0]]
    else:
        for i, clock in enumerate(clocks):
            if i + 1 in indexs:
                chooseds.append(clock)
    
    # switch them
    for clock in chooseds:
        clock.switch()
        if isinstance(clock, OnceClock):
            clocks.remove(clock)
    return

def _getFirstRemindOrExpired(_clocks, now):
    for clock in _clocks:
        if clock.checkRemind(now):
            return clock
    for clock in _clocks:
        if clock.isExpired():
            return clock
    return None

@synchronized(_clock_lock)
def remove(indexs):
    remain = []
    for i, clock in enumerate(clocks):
        if i + 1 not in indexs:
            remain.append(clock)
    for i in range(len(clocks)):
        clocks.pop()
    clocks.extend(remain)
    return

@synchronized(_clock_lock)
def later(time):
    '''延迟到 time 的时间再提醒，分2种情况:
    存在提醒闹钟: 设置他们的提醒时间；
    不存在: 设置所有到期闹钟的提醒时间'''
    reminds = getReminds()
    if len(reminds):
        for clock in reminds:
            clock['remindTime'] = time
    else:
        now = getNow()
        for clock in clocks:
            if clock.isExpired():
                clock['remindTime'] = time
    return

@synchronized(_clock_lock)
def resortAndSave():
    clocks.sort(key=_sort)
    with open(_data_filepath, 'w') as file:
        for clock in clocks:
            file.write(repr(clock))
            file.write('\n')
    return

@synchronized(_clock_lock)
def refreshWeekly():
    '''刷新星期重复闹钟。目的是让设置时间停留在过去的闹钟重新从今天开始计算下次时间。
    跳过到期闹钟，即响铃后重启程序不会自动刷新。'''
    for clock in clocks:
        if isinstance(clock, WeeklyClock) and not clock['expired']:
            clock.refresh(clock['time'])

_init()
