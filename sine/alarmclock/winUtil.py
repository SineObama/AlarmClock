# coding=utf-8
'''
windows 窗口相关的辅助接口函数。
提供任务栏闪烁、显示隐藏窗口、置顶窗口等。
依赖于 win32api 和 win32gui 。
'''

import win32api
import win32gui
from . import mylogging

logger = mylogging.getLogger(__name__)

hWnd = 0

def refreshWindow():
    '''refresh window's handle (HWND)'''
    global hWnd
    s = win32api.GetConsoleTitle()
    hWnd = win32gui.FindWindow(0, s)

def refreshOnError(func):
    def refreshOnErrorWrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except Exception as e:
            logger.warn("run window function fail. trying again...", exc_info=1)
            return func(*args, **kw)
    return refreshOnErrorWrapper

@refreshOnError
def flash(dwFlags=3, uCount=5, dwTimeout=500):
    '''
    @see  http://timgolden.me.uk/pywin32-docs/win32gui__FlashWindowEx_meth.html

    flash the window a specified number of times.

    @param  dwFlags     integer, Combination of win32con.FLASHW_* flags
    @param  uCount      integer, Nbr of times to flash
    @param  dwTimeout   integer, Elapsed time between flashes, in milliseconds

    @more
    flags:
    FLASHW_STOP         0000
    FLASHW_CAPTION      0001
    FLASHW_TRAY         0010
    FLASHW_ALL          0011
    FLASHW_TIMER        0100
    FLASHW_TIMERNOFG    1100
    '''
    win32gui.FlashWindowEx(hWnd, dwFlags, uCount, dwTimeout)

@refreshOnError
def stopFlash():
    '''stop the flashing before it finish, but not discard the highlight.'''
    flash(0, 0, 0)

@refreshOnError
def show(swFlag):
    win32gui.ShowWindow(hWnd, swFlag)

@refreshOnError
def isForeground():
    return win32gui.GetForegroundWindow() == hWnd

@refreshOnError
def setForeground():
    try:
        win32gui.SetForegroundWindow(hWnd)
    except Exception as e:
        pass

@refreshOnError
def bringToTop():
    win32gui.BringWindowToTop(hWnd)

refreshWindow()
