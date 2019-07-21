# coding: utf-8
'''管理页面和输入'''

# 外部依赖
import sys
import datetime
import os
import threading
# library依赖
from plone.synchronize import synchronized
from sine.utils import ReStartableThread
# 本地依赖
from .globalData import clocks, data, config, eManager, title
from .parsing import *
from .mydatetime import getNow, getNextFromWeekday, getNextAfterNow
from .entity import AlarmClock, OnceClock, WeeklyClock, PeriodClock
from .exception import ClientException, NoStringException
from . import formatter
from . import player
from . import mylogging
from . import manager

logger = mylogging.getLogger(__name__)

alarmInterval = datetime.timedelta(0, config['alarm_interval'])
fmt = formatter.create(config, config['format'])
on_str = config['state.ON']
off_str = config['state.OFF']
write = sys.stdout.write

'''
使用“栈”管理页面
每个页面有2个函数接口: 
reprint 输出页面（先清屏）
execute 接受指令，根据返回值进行操作，分3种情况:
0: 退出页面
-1: 无操作
其他: 执行对应函数（函数以字典保存在页面中）
'''
class Page(dict):
    def execute(self):
        return 0
    def reprint(self):
        pass
stack = []
stack_lock = threading.RLock()
@synchronized(stack_lock)
def append(page):
    stack.append(page)
    cls()
    page.reprint()
    return
@synchronized(stack_lock)
def pop(cls=None):
    rtn = None
    if len(stack) and (cls == None or isinstance(stack[-1], cls)):
        rtn = stack.pop()
    reprintTop()
    return rtn

def cls():
    if not config['debug.no_clear_screen']:
        os.system('cls')
    return

def trigger_clock_change():
    eManager.sendEvent('clock_change')

def reprintTop(*args, **kw):
    '''重新输出顶层页面，无页面时无操作'''
    top = None
    try:
        top = stack[-1]
    except Exception as e:
        pass
    if top:
        cls()
        top.reprint()

def saveAndReprint(*args, **kw):
    manager.resortAndSave()
    eManager.sendEvent('clock_sort')


# 主页面 ---------------- 闹钟列表

class MainPage(Page):

    def __init__(self):
        self[1] = trigger_clock_change

    def reprint(self):
        now = getNow()
        if len(clocks):
            write(u'闹钟: ')
        else:
            write(u'无闹钟')
        write(u'\t(声音: ' + (u'开' if data['sound'] else u'关'))
        write(u', 消息提示: ' + (u'开' if data['show_msg'] else u'关') + ')\n')
        isToday = True
        on = True
        today = datetime.datetime.date(now)
        for i, clock in enumerate(clocks):
            if isToday and datetime.datetime.date(clock['time']) > today and clock['on']:
                isToday = False
                write(u'明天之后:\n')
            if on and not clock['on']:
                on = False
                write(u'已关闭:\n')
            write(fmt(i+1, clock) + '\n')
        return
    
    def execute(self, order):
        now = getNow()
        try: # catch parse exception
            if len(order) == 0: # 'later' and clean screen
                manager.later(now + alarmInterval)
                return 1

            order = order.strip()
            if order == 'q': # quit
                return 0
            if order == 'd': # switch quiet
                data['sound'] = not data['sound']
                eManager.sendEvent('sound.change')
                return -1
            if order.startswith('z') and config['debug']: # debug
                exec(order[1:])
                return -1

            # edit clock in new page
            if order.startswith('e'):
                index, unused = parseInt(order[1:], 0)
                append(EditPage(manager.get(index, True)))
                return -1
            # edit time
            if order.startswith('w'):
                index, remain = parseInt(order[1:])
                target, unused = parseDateTime(remain, now)
                target = getNextAfterNow(now, target)
                manager.editTime(manager.get(index), target)
                return 1
            # cancel alarm
            if order.startswith('a'):
                index, unused = parseInt(order[1:], 0)
                manager.cancel(manager.get(index))
                return 1
            # switch
            if order.startswith('s'):
                indexs = parseAllToIndex(order[1:])
                manager.switch(indexs)
                return 1
            # remove clock
            if order.startswith('r'):
                indexs = parseAllToIndex(order[1:])
                manager.remove(indexs)
                return 1
            
            # $dtime ($msg)        #一次性闹钟
            # $dtime w$wday ($msg)        #星期重复闹钟
            # $dtime r$dtime ($msg)        #周期重复闹钟
            target, remain = parseDateTime(order, now)
            try:
                second = ''
                second, remain2 = parseString(remain)
            except NoStringException as e:
                pass
            if second.startswith('w'):
                weekdays, msg = parseString(remain[1:])
                target = getNextFromWeekday(now, target, weekdays)
                manager.add(WeeklyClock({'time':target,'weekdays':weekdays,'msg':msg}))
                return 1
            if second.startswith('r'):
                period, msg = parseDateAndTime(remain[1:], zero)
                period -= zero
                manager.add(PeriodClock({'time':target,'period':period,'msg':msg}))
                return 1
            target = getNextAfterNow(now, target)
            manager.add(OnceClock({'time':target,'msg':remain}))
            return 1
        except ClientException as e:
            e.printMsg()
            return -1

# 编辑页面 ----------------

class EditPage(Page):

    def __init__(self, clock):
        self.clock = clock
        self[1] = trigger_clock_change
        self[2] = reprintTop
    
    def reprint(self):
        clock = self.clock
        write(u' - 编辑 - \n')
        write('%s\n' % (on_str if clock['on'] else off_str))
        write(u'下个时间: %s\n' % str(clock['time']))
        write(u'提前响铃: %s\n' % str(clock['remindAhead']))
        write(u'重复类型: ')
        if isinstance(clock, OnceClock):
            write(u'一次性')
        else:
            if isinstance(clock, WeeklyClock):
                write(u'每星期 ')
                weekdays = clock.repeatStr()
                write(u'不重复' if weekdays.isspace() else weekdays)
            else:
                write(u'每隔 ' + clock.repeatStr())
        write(u'\n')
        write(u'信息: ')
        write(clock['msg'] + '\n')
        write(u'铃声: ')
        write(clock['sound'] + '\n')
        return
    
    def execute(self, order):
        clock = self.clock
        try: # catch parse exception
            order = order.strip()
            if order == 'q': # quit
                return 0

            # edit time
            if order.startswith('w'):
                target, unused = parseDateTime(order[1:], getNow())
                target = getNextAfterNow(now, target)
                clock.editTime(target)
                manager.save(clock)
                return 1
            # edit remind ahead
            if order.startswith('a'):
                ahead = parseInt(order[1:])[0]
                if ahead < 0:
                    raise ClientException(u'不能使用负数。')
                clock.editRemindAhead(ahead)
                return 1
            # edit message
            if order.startswith('m'):
                clock['msg'] = order[1:].strip()
                return 1
            # edit repeat time
            if order.startswith('r'):
                if isinstance(clock, OnceClock):
                    raise ClientException(u'此闹钟无法重复。')
                if isinstance(clock, WeeklyClock):
                    clock.editWeekdays(parseString(order[1:])[0])
                else:
                    period, unused = parseDateAndTime(order[1:], zero)
                    clock.editPeriod(period - zero)
                    clock.resetTime(getNow() + clock['period'])
                return 1
            # edit sound
            if order.startswith('s'):
                fname = order[1:].strip()
                player.assertLegal(fname)
                clock['sound'] = fname
                return 1
            
            return 2
        except ClientException as e:
            e.printMsg()
            return -1

# 响铃页面 -----------------

class AlarmPage(Page):

    def __init__(self):
        self[1] = manager.resortAndSave

    def execute(self, order):
        order = order.strip()
        now = getNow()
        if len(order) == 0: # 'later' and clean screen
            manager.later(now + alarmInterval)
            return 1
        # cancel alarm
        if order == 'a':
            manager.cancel(None)
            return 1
        # switch
        if order == 's':
            manager.switch([])
            return 1
        return -1


# 事件监听 ------------------

# 页面 -----------------

def wake(data):
    manager.refreshWeekly()
    saveAndReprint()
eManager.addListener('alarm.start', lambda data:append(AlarmPage()))
eManager.addListener('time_leap', wake)
eManager.addListener('cross_day', saveAndReprint)
eManager.addListener('sound.change', reprintTop)
eManager.addListener('clock_sort', reprintTop)
eManager.addListener('show_msg.change', reprintTop)
eManager.addListener('clock_change', saveAndReprint)

# 页面文字闪烁 ---------------- 通过清屏和重新输出

def _screen(stop_event):
    fmt = formatter.create(config, config['flash_format'])
    tokens = config['screen_flash_mode']
    sleep_len = 1.0 / len(tokens)
    pos = 0
    last = '2'
    while not stop_event.wait(sleep_len):
        if pos >= len(tokens):
            pos = 0
            last = '2' # 使之更新列表
        if last != tokens[pos]:
            last = tokens[pos]
            if last == '0':
                cls()
            elif last == '1':
                reminds = manager.getReminds() # 获取需要闹铃提醒的闹钟
                string = ''
                for i, clock in enumerate(reminds):
                    string += fmt(i+1, clock) + '\n'
                write(string)
        pos += 1
    return

_screenThread = ReStartableThread(target=_screen)
eManager.addListener('alarm.start', lambda data:_screenThread.start())
def stopScreenFlashAndReprint(key):
    _screenThread.stop()
    pop(AlarmPage)
eManager.addListener('alarm.stop', stopScreenFlashAndReprint)
eManager.addListener('alarm.timeout', stopScreenFlashAndReprint)


def mainLoop():
    try:
        os.system(u'title ' + title)
        append(MainPage())
        while (1):
            order = input().lower()
            logger.info('order: ' + order)
            try:
                page = stack[-1]
                rtn = page.execute(order)
                if rtn == 0:
                    pop()
                elif rtn != -1:
                    page[rtn]()
            except Exception as e:
                logger.warn('exception.', exc_info=1)
            if len(stack) == 0:
                eManager.sendEvent('quit', {'from':'user interface'})
                break
    except:
        logger.warn('exception.', exc_info=1)
