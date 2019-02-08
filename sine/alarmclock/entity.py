# coding=utf-8
'''闹钟实体，也有一些表现差异的逻辑代码'''

import datetime
from . import mydatetime
from .mydatetime import *
from .parsing import zero
from .globalData import data, config, eManager
from .exception import ClockException

class AlarmClock(dict):
    '''
    闹钟基类。字段如下:
    time:datetime.datetime      闹钟时间
    expired:Boolean             是否到期/提醒过
    remindTime:datetime.datetime 提醒时间（响铃时间）
    remindAhead:datetime.timedelta 提前提醒时间（比如1分钟）
    msg:Str                     信息
    on:Boolean                  开关
    sound:Str                   铃声，见 player 模块'''
    def __init__(self, dic):
        '''必须含义time字段'''
        self.update(dic)
        if 'time' not in self:
            raise ClockException(u'内部错误，找不到闹钟时间。')
        self.setdefault('msg', '')
        self.setdefault('expired', False)
        self.setdefault('remindAhead', datetime.timedelta(0, config['default_remindAhead']))
        self.setdefault('remindTime', dic['time'] - self['remindAhead'])
        self.setdefault('on', True)
        self.setdefault('sound', config['default_sound'])
    
    def __repr__(self):
        return self.__class__.__name__ + '(' + dict.__repr__(self) + ')'

    def __str__(self):
        return self['time'].strftime('%Y-%m-%d %H:%M:%S') + ' ' + self['msg']
    
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return None

    def checkRemind(self, now):
        '''如果需要提醒则会开启过期状态。
        返回是否需要提醒。'''
        if self['on'] and self['remindTime'] <= now:
            if self['expired'] == False:
                eManager.sendEvent('clock.remind', self)
            self['expired'] = True
            return True
        return False

    def isExpired(self):
        '''是否提醒过'''
        return self['on'] and self['expired']
    
    def resetTime(self, time):
        '''设置时间。会级联更新一些字段'''
        self['time'] = time
        self['remindTime'] = time - self['remindAhead']
        self['expired'] = False

    def repeatStr(self):
        '''获取自身重复内容'''
        return ''

    def editTime(self, date_time):
        '''会开启闹钟。'''
        self.resetTime(date_time)
        self['on'] = True
        self['expired'] = False

    def cancel(self):
        '''取消闹钟，不同类型的闹钟可能有一些连带效应。'''
        self['on'] = False

    def switch(self):
        self['on'] = not self['on']
        self['expired'] = False

    def editRemindAhead(self, seconds):
        self['remindAhead'] = datetime.timedelta(0, seconds)
        self['remindTime'] = self['time'] - self['remindAhead']
        self['expired'] = False

class OnceClock(AlarmClock):
    '''一次性闹钟，取消后会被删除'''
    def switch(self):
        self['on'] = False

class WeeklyClock(AlarmClock):
    '''
    星期重复闹钟，无重复设置时取消后自动关闭。额外字段:
    weekdays:string 格式如: '12345  ', '1 3 567'
    '''
    def __init__(self, dic):
        AlarmClock.__init__(self, dic)
        if 'weekdays' not in self:
            raise ClockException(u'内部错误，找不到星期。')
        self['weekdays'] = formatWeekdays(self['weekdays'])

    def refresh(self, time=None):
        '''更新时间，在今天或 time 之后重新开始计算，但会确保比现在晚。'''
        now = getNow()
        if time != None:
            self.resetTime(getNextFromWeekday(now, time, self['weekdays']))
        else:
            self.resetTime(getNextFromWeekday(now, self['time'], self['weekdays'], True))

    def editWeekdays(self, weekdays):
        '''修改星期。会格式化输入'''
        self['weekdays'] = formatWeekdays(weekdays)
        self.refresh(self['time'])

    def repeatStr(self):
        return self['weekdays']

    def editTime(self, date_time):
        '''如果时间不在重复周期上，会自动往后推。'''
        AlarmClock.editTime(self, getNextFromWeekday(getNow(), date_time, self['weekdays']))

    def cancel(self):
        '''取消下一个提醒，时间顺延往后'''
        if self['weekdays'].isspace():
            self['on'] = False
        else:
            self.refresh(self['time'] + day)

    def switch(self):
        '''会从现在开始重新计算下一次时间'''
        AlarmClock.switch(self)
        self.refresh()

class PeriodClock(AlarmClock):
    '''
    周期重复闹钟
    period:datetime.timedelta 间隔时间（比如1小时）
    '''
    def __init__(self, dic):
        AlarmClock.__init__(self, dic)
        if 'period' not in self:
            raise ClockException(u'内部错误，找不到周期。')
        self.editPeriod(dic['period'])

    def editPeriod(self, period):
        '''修改周期'''
        if not period:
            raise ClockException(u'周期不能为0。')
        self['period'] = period

    def repeatStr(self):
        return (zero + self['period']).strftime('%H:%M:%S')
        
    def cancel(self):
        '''从现在重新开始计时'''
        self.resetTime(getNow() + self['period'])

    def switch(self):
        '''开启时如果过期，则以当前时间重新开始计时'''
        AlarmClock.switch(self)
        now = getNow()
        if self['on'] and self['time'] < now:
            self.resetTime(now + self['period'])
