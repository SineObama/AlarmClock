# coding=utf-8
'''
taskbar flashing and window showing helpers on windows.

depend on package win32api and win32gui.
'''

import win32api
import win32gui

hWnd = 0

def refreshWindow():
    '''refresh window's handle (HWND)'''
    global hWnd
    s = win32api.GetConsoleTitle()
    hWnd = win32gui.FindWindow(0, s)

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

def stopFlash():
    '''stop the flashing before it finish, but not discard the highlight.'''
    flash(0, 0, 0)

def show(swFlag):
    win32gui.ShowWindow(hWnd, swFlag)

def setForeground():
    try:
        win32gui.SetForegroundWindow(hWnd)
    except Exception as e:
        pass

refreshWindow()
