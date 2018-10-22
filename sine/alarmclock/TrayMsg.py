#coding: utf-8
'''以托盘图标的方式发出右下角的提示信息。'''
# 原来源: http://angeloce.iteye.com/blog/493681

import win32gui
import win32con
import time
import threading
from sine.threads import ReStartableThread

class TrayMsg:
    count = 0
    lock = threading.Lock() # 共享变量count锁
    def __init__(self, hicon, LC, AC):
        self.LC=LC
        self.AC=AC
        # 注册一个窗口类
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32gui.GetModuleHandle(None)
        TrayMsg.lock.acquire()
        self.className = wc.lpszClassName = "TrayMsg" + str(TrayMsg.count)
        TrayMsg.count += 1
        TrayMsg.lock.release()
        wc.lpfnWndProc = self.WndProc
        classAtom = win32gui.RegisterClass(wc)
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow( classAtom, self.className, style,
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                0, 0, hinst, None)
        if hicon == None:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        self.hicon = hicon
        nid = (self.hwnd, 0, win32gui.NIF_ICON, win32con.WM_USER+20, hicon, self.className)
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

    def showMsg(self, title, msg):
        # 原作者使用Shell_NotifyIconA方法代替包装后的Shell_NotifyIcon方法
        # 据称是不能win32gui structure, 我稀里糊涂搞出来了.
        # 具体对比原代码.
        nid = (self.hwnd, # 句柄
                0, # 托盘图标ID
                win32gui.NIF_INFO, # 标识
                0, # 回调消息ID
                self.hicon, # 托盘图标句柄
                "TestMessage", # 图标字符串
                msg, # 气球提示字符串
                0, # 提示的显示时间
                title, # 提示标题
#                 win32gui.NIIF_INFO # 提示用到的图标
                )
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)

    def WndProc(self, hwnd, msg, wParam, lParam):
        # 经过试验得到这2个参数，分别代表点击了消息窗口（然后窗口关闭了）和窗口自动关闭。
        # 在以上情况下关闭窗口
        if lParam == win32con.WM_PSD_ENVSTAMPRECT:
            self.LC(self)
        if lParam == win32con.WM_PSD_GREEKTEXTRECT:
            self.AC(self)
        if msg == win32con.WM_DESTROY:
            nid = (self.hwnd, 0)
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
            win32gui.PostQuitMessage(0) # Terminate the app.
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

def _nothing(*args, **kw):
    pass

def send(title, msg, hicon=None, LC=_nothing, AC=_nothing):
    '''最后2个分别是回调: 左键点击消息框或图标（框会关闭），消息自动消失。回调参数为TrayMsg对象。'''
    def thread():
        t = TrayMsg(hicon, LC, AC)
        className = t.className
        t.showMsg(title, msg)
        def thread2():
            try:
                time.sleep(10)
                win32gui.PostMessage(t.hwnd, win32con.WM_CLOSE, 0, 0)
                time.sleep(0.5)
            except Exception as e:
                pass
        ReStartableThread(target=thread2).start()
        win32gui.PumpMessages()
        try:
            win32gui.UnregisterClass(className, 0)
        except Exception as e:
            pass
    ReStartableThread(target=thread).start()
