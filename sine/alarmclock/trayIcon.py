# coding=utf-8
'''
创建一个托盘图标，会监听事件改变图标、悬浮文字，右键菜单也会动态改变，同时支持消息提示（右下角弹框）。
悬浮文字: 显示声音、消息提示的开关状态，然后正常显示今日闹钟，有提醒时则显示到期闹钟。
单击时显示并置顶/隐藏窗口。

用完记得删除。
基于网上代码模块 SysTrayIcon （图标）， TrayMsg （消息提示），都有过修改。
'''
import win32gui
import win32con
import sys
import time
from threading import Thread, Lock
from .SysTrayIcon import SysTrayIcon
from .TrayMsg import send
from .globalData import clocks, data, config, useDefault, eManager, title
from sine.utils import ReStartableThread
from . import winUtil
from . import manager
from .mydatetime import *
from . import mylogging

logger = mylogging.getLogger(__name__)

def _init():
    # 加载图标
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
    read('msg.ico')

alarmInterval = datetime.timedelta(0, config['alarm_interval'])
showWindow = True

# 菜单回调函数 -------------

def _onQuit(*args):
    eManager.sendEvent('quit', {'from':'icon menu'})

def _switchQuiet(*args):
    data['sound'] = not data['sound']
    eManager.sendEvent('sound.change')

def _switchShowMsg(*args):
    data['show_msg'] = not data['show_msg']
    eManager.sendEvent('show_msg.change')

def _later(*args):
    manager.later(getNow() + alarmInterval)

def _onLeftClick(*args):
    global showWindow
    if len(manager.getReminds()) > 0:
        manager.later(getNow() + alarmInterval)
    else:
        if showWindow:
            if foregroundRecord.count(True) > 3:
                showWindow = False
                winUtil.show(0)
            else:
                winUtil.bringToTop()
                winUtil.setForeground()
        else:
            showWindow = True
            winUtil.show(1)
            winUtil.bringToTop()
            winUtil.setForeground()

def _createCloser(clock):
    '''创建取消对应闹钟的回调函数'''
    def closer(*args, **kwargs):
        manager.cancel(clock)
        eManager.sendEvent('clock_change', {'clock':clock})
    return closer

def _addition_menu():
    '''动态添加额外的右键菜单选项，实现对菜单文字的更改和取消闹钟（显示到期闹钟，没有则显示今日闹钟）。'''
    result = []
    # 取消（停止）提醒闹钟，或者提前取消今日闹钟
    predicate = u'停止 '
    clocks = manager.getExpired()
    if len(clocks) == 0:
        predicate = u'取消 '
        clocks = getTodayClock()
    texts = _clocksToStrings(clocks)
    for i in range(len(clocks)):
        result.append((predicate + texts[i], None, _createCloser(clocks[i])))
    
    # 声音和消息提示的开关
    result.append(((u'关闭' if data['sound'] else u'开启') + u'声音', None, _switchQuiet))
    result.append(((u'关闭' if data['show_msg'] else u'开启') + u'消息提示', None, _switchShowMsg))
    return result

def getTitle():
    return title + "\n" + \
    u'声音: ' + (u'开' if data['sound'] else u'关') + '\n' + \
    u'消息提示: ' + (u'开' if data['show_msg'] else u'关')

menu_options = [(u'延迟', None, _later)] # 静态菜单

_data = {'instance':None, 'exist':False} # 全局数据
_lock = Lock() # 对以上状态数据的锁

def createIcon():
    _lock.acquire()
    if _data['exist']:
        _lock.release()
        return
    def mainLoop():
        try:
            _data['instance'] = SysTrayIcon('clock.ico', getTitle(), tuple(menu_options), _onLeftClick, _addition_menu, on_quit=_onQuit)
            _data['exist'] = True
        finally:
            created = _data['exist']
            _lock.release()
            if created:
                _reset_icon()
                win32gui.PumpMessages()
    trayThread = Thread(target=mainLoop)
    trayThread.start()

def deleteIcon():
    '''退出时的清理: 删除图标（关闭窗口），并尝试注销窗口类。'''
    _lock.acquire()
    if not _data['exist']:
        _lock.release()
        return
    try:
        # 关闭窗口
        try:
            win32gui.PostMessage(_data['instance'].hwnd, win32con.WM_CLOSE, 0, 0)
        except Exception as e:
            if not hasattr(e, '__getitem__') or e[0] == 1400:
                # (1400, 'PostMessage', '\xce\xde\xd0\xa7\xb5\xc4\xb4\xb0\xbf\xda\xbe\xe4\xb1\xfa\xa1\xa3')
                # 无效的窗口句柄。
                # 这个情况一般是因为通过托盘图标退出，窗口就没有了，这时主程序再清理
                pass
            else:
                raise

        # 注销窗口类
        tryTimes = 5
        for i in range(tryTimes):
            try:
                win32gui.UnregisterClass(_data['instance'].window_class_name, 0)
                break
            except Exception as e:
                if not hasattr(e, '__getitem__') or e[0] == 1412:
                    # (1412, 'UnregisterClass', '\xc0\xe0\xc8\xd4\xd3\xd0\xb4\xf2\xbf\xaa\xb5\xc4\xb4\xb0\xbf\xda\xa1\xa3')
                    # 类仍有打开的窗口。
                    # 这个情况一般是因为消息传递和窗口关闭的异步延迟
                    pass
                else:
                    raise
            time.sleep(0.1)
    except:
        logger.warn('exception in deleteIcon, ignored.', exc_info=1)
        pass
    finally:
        _data['instance'] = None
        _data['exist'] = False
        _lock.release()

def _refresh_icon(icon, hover_text):
    _lock.acquire()
    try:
        if not _data['exist']:
            return
        _data['instance'].refresh_icon2(icon, hover_text)
    except Exception as e:
        pass
    finally:
        _lock.release()

def getTodayClock():
    today_clocks = []
    today = datetime.datetime.date(getNow())
    for clock in clocks:
        if datetime.datetime.date(clock['time']) == today and clock['on']:
            today_clocks.append(clock)
    return today_clocks

def _reset_icon(*ua, **uk):
    '''刷新为常驻图标，更新悬浮文字。参数无用。'''
    _refresh_icon(data['clock.ico'] if data['sound'] else data['quiet.ico'],
                  getTitle() + '\n' + '\n'.join(_clocksToStrings(getTodayClock())))

def _clocksToStrings(_clocks, maxLen=24):
    '''把闹钟拼接为多行文本，没有则返回无闹钟。其中限制闹钟内容的长度为 maxLen 。'''
    texts = []
    for clock in _clocks:
        msg = clock['msg']
        if len(msg) > maxLen:
            msg = msg[:maxLen] + '...'
        texts.append(clock['time'].strftime("%H:%M ") + msg)
    if len(texts) == 0:
        texts.append(u'今日无闹钟')
    return texts

def _listen(stop_event):
    '''实现托盘图标闪烁'''
    iconFlash = False
    flag = True
    while not stop_event.wait(0.25):
        # 获取到期的闹钟，托盘闪烁和显示
        expired = manager.getExpired()
        if len(expired) > 0:
            if not iconFlash:
                iconFlash = True
                flag = True
            _refresh_icon(None if flag else data['alarm.ico'],
                          getTitle() + u'\n【提醒中】\n' + '\n'.join(_clocksToStrings(expired)))
            flag = not flag
        elif iconFlash:
            iconFlash = False
            _reset_icon()

foregroundRecord = [False, False, False, False, False]
def _record(stop_event):
    '''记录最近的时刻，窗口是否在最前'''
    while not stop_event.wait(0.1):
        foregroundRecord.insert(0, winUtil.isForeground())
        foregroundRecord.pop()

def closeAndLater(tray):
    win32gui.DestroyWindow(tray.hwnd)
    manager.later(getNow() + alarmInterval)
def _showMsg(key, clock):
    '''消息提示'''
    if data['show_msg']:
        send(clock['msg'],
            str(clock['time'].strftime('%H:%M')),
            data['msg.ico'],
            closeAndLater)

_init()

_listenThread = ReStartableThread(target=_listen)
_listenThread.start()
_recordThread = ReStartableThread(target=_record)
_recordThread.start()

eManager.addListener('sound.change', _reset_icon)
eManager.addListener('clock_sort', _reset_icon)
eManager.addListener('clock.remind', _showMsg)
