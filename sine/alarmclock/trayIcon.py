# coding=utf-8
'''
创建一个托盘图标（先在menu_options设置菜单），并可以更新图标和悬浮文字，用完记得删除。
'''
import win32gui
import win32con
import sys
from SysTrayIcon import SysTrayIcon
from data import data, useDefault
from sine.threads import ReStartableThread
import winUtil
import manager
from mydatetime import *
from initUtil import invalid

def _init():
    hinst = win32gui.GetModuleHandle(None)
    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    def read(filename):
        useDefault(data['location'], filename)
        data[filename] = win32gui.LoadImage(hinst,
                                   filename,
                                   win32con.IMAGE_ICON,
                                   0,
                                   0,
                                   icon_flags)
    read('clock.ico')
    read('alarm.ico')
    read('quiet.ico')

quitEvent = None
refresh = invalid

def setQuitEvent(event):
    global quitEvent
    quitEvent = event

def setRefresh(func):
    global refresh
    refresh = func

def _onQuit(*args):
    quitEvent.set()

def _switchQuiet(*args):
    data['quiet'] = not data['quiet']
    _reset_icon()

alarmInterval = datetime.timedelta(0, data['config']['alarm_interval'])
def _later(*args):
    manager.later(getNow() + alarmInterval)

showWindow = True

def _onLeftClick(*args):
    global showWindow
    showWindow = not showWindow
    winUtil.show(int(showWindow))
    if showWindow:
        winUtil.setForeground()

def createCloser(clock):
    def closer(*args, **kwargs):
        manager.cancel(clock)
        manager.resortAndSave()
        refresh()
    return closer

def _addition_menu():
    result = []
    clocks = manager.getExpired()
    texts = _clocksToStrings(clocks)
    for i in range(len(clocks) - 1, -1, -1):
        result.append(('close \'' + texts[i] + '\'', None, createCloser(clocks[i])))
    return result

def getTitle():
    return u"闹钟" + (u' - 静音' if data['quiet'] else '')

icons = 'clock.ico'
menu_options = [('later', None, _later),
                ('quiet', None, _switchQuiet)]

_data = {'instance':None, 'exist':False}

def createIcon():
    def mainLoop(stop_event):
        _data['instance'] = SysTrayIcon(icons, getTitle(), tuple(menu_options), _onLeftClick, _addition_menu, on_quit=_onQuit)
        _data['exist'] = True
        _reset_icon()
        win32gui.PumpMessages()
    trayThread = ReStartableThread(target=mainLoop)
    trayThread.start()

def deleteIcon():
    # the window may be left
    _data['exist'] = False
    try:
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (_data['instance'].hwnd,))
    except Exception as e:
        pass

def _refresh_icon(icon, hover_text):
    if not _data['exist']:
        return
    try:
        _data['instance'].refresh_icon2(icon, hover_text)
    except Exception as e:
        pass

def _reset_icon():
    '''正常情况显示当日闹钟'''
    clocks = []
    today = datetime.datetime.date(getNow())
    for clock in data['clocks']:
        if datetime.datetime.date(clock['time']) > today:
            break
        clocks.append(clock)
    _refresh_icon(data['quiet.ico'] if data['quiet'] else data['clock.ico'], getTitle() + '\n' + '\n'.join(_clocksToStrings(clocks)))

def _clocksToStrings(clocks):
    '''把闹钟拼接为多行文本'''
    texts = []
    for clock in clocks:
        texts.append(clock['time'].strftime("%H:%M ") + clock['msg'].decode(sys.stdout.encoding))
    if len(texts) == 0:
        texts.append(u'今日无闹钟')
    return texts

def _listen(stop_event):
    iconFlash = False # 托盘图标闪烁
    flag = True
    while not stop_event.wait(0.25):
        # 获取到期的闹钟，托盘闪烁和显示
        expired = manager.getExpired()
        if len(expired) > 0:
            if not iconFlash:
                iconFlash = True
                flag = True
            _refresh_icon(None if flag else data['alarm.ico'], getTitle() + '\n' + '\n'.join(_clocksToStrings(expired)))
            flag = not flag
        elif iconFlash:
            iconFlash = False
            _reset_icon()

_init()

_listenThread = ReStartableThread(target=_listen)
_listenThread.start()

manager.change_callback = _reset_icon
