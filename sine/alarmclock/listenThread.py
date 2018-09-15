# coding=utf-8
'''
监听线程。检查闹钟状态并进行屏幕闪烁和播放铃声。
需要设置回调函数：响铃启动on、关闭off、刷新列表refresh。
提供start和stop接口，可重复启动。
'''

import datetime
import time
import manager
from data import data
from initUtil import warn, invalid
from mydatetime import getNow
config = data['config']

alarmLast = config['alarm_last']
alarmInterval = datetime.timedelta(0, config['alarm_interval'])
on = lambda:None
off = lambda:None
refresh = lambda:None # 刷新闹钟列表

def _listen(stop_event):
    import player
    count = 0
    alarm = False # “闹铃”提醒状态

    prev = getNow()
    minGap = datetime.timedelta(0, 300) # 超过300秒，认为是睡眠/待机唤醒
    while 1:
        if stop_event.is_set():
            break

        # 检查睡眠唤醒和跨越凌晨
        cur = getNow()
        if cur - prev >= minGap:
            manager.refreshWeekly()
            manager.resortAndSave()
            refresh()
        elif datetime.datetime.date(cur) != datetime.datetime.date(prev):
            refresh()
        prev = cur

        # 获取需要闹铃提醒的闹钟
        reminds = manager.getReminds()
        length = len(reminds)
        player.play(reminds[0]['sound'] if length else None)
        
        # 响铃状态切换
        if not alarm and length:
            alarm = True
            flash(3, alarmLast, 500)
            _screenThread.start()
            on()
            count = 0
        if alarm and not len(reminds):
            alarm = False
            player.play(None)
            stopFlash()
            _screenThread.stop()
            off()
        if alarm and count > 10 * alarmLast:
            alarm = False
            player.play(None)
            _screenThread.stop()
            manager.later(getNow() + alarmInterval) # 推迟提醒
            off()
        count += 1
        time.sleep(0.1)
    player.play(None)
    stopFlash()
    return

from sine.threads import ReStartableThread

_listenThread = ReStartableThread(target=_listen)

def start():
    _listenThread.start()

def stop():
    _listenThread.stop()
    _listenThread.join(1)

try:
    if config['taskbar_flash']:
        from winUtil import flash, stopFlash
except ImportError, e:
    warn('taskbar flashing not supported.', e)
    flash = stopFlash = invalid

def _screen(stop_event):
    import os
    import formatter
    fmt = formatter.create(config, config['flash_format'])
    tokens = config['screen_flash_mode']
    sleep_len = 1.0 / len(tokens)
    pos = 0
    last = '2'
    while 1:
        if stop_event.is_set():
            break
        if pos >= len(tokens):
            pos = 0
            last = '2' # 使之更新列表
        if last != tokens[pos]:
            last = tokens[pos]
            if last == '0':
                os.system('cls')
            elif last == '1':
                reminds = manager.getReminds() # 获取需要闹铃提醒的闹钟
                string = ''
                for i, clock in enumerate(reminds):
                    string += fmt(i+1, clock) + '\n'
                print string
        pos += 1
        time.sleep(sleep_len)
    return

_screenThread = ReStartableThread(target=_screen)
