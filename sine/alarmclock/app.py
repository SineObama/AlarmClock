# coding: utf-8
'''程序主要部分'''

# 外部依赖
import datetime
import threading
# library依赖
from sine.utils import ReStartableThread
# 本地依赖
from .globalData import clocks, data, config, eManager
from .mydatetime import getNow
from . import initUtil
from . import player
from . import mylogging
from . import manager
from . import userInterface

logger = mylogging.getLogger(__name__)

alarmInterval = datetime.timedelta(0, config['alarm_interval'])
alarmLast = config['alarm_last']

# 监听线程，检查并更新闹钟状态

def _listen(stop_event):
    startTime = None

    prev = getNow()
    minGap = datetime.timedelta(0, 300) # 超过300秒，认为是睡眠/待机唤醒
    while not stop_event.wait(0.1):
        # 检查睡眠唤醒和跨越凌晨
        cur = getNow()
        gap = cur - prev
        if gap >= minGap:
            eManager.sendEvent('time_leap', {'gap':gap})
            stop_event.wait(1) # sleep
        elif datetime.datetime.date(cur) != datetime.datetime.date(prev):
            eManager.sendEvent('cross_day')
        prev = cur

        # 获取需要闹铃提醒的闹钟
        reminds = manager.getReminds()
        length = len(reminds)
        player.play(reminds[-1]['sound'] if length else None)
        
        # 响铃状态切换
        if startTime == None and length:
            startTime = getNow()
            eManager.sendEvent('alarm.start')
        if startTime and not length:
            startTime = None
            eManager.sendEvent('alarm.stop')
        if startTime and (getNow() - startTime).seconds > alarmLast:
            startTime = None
            eManager.sendEvent('alarm.timeout')
    return

listenThread = ReStartableThread(target=_listen)

# 托盘图标 -----------------

try:
    from .trayIcon import createIcon, deleteIcon
except Exception as e:
    initUtil.warn(u'不支持托盘图标（包括消息提示）。', e)
    createIcon = deleteIcon = initUtil.doNothing
    data['show_msg'] = False

# 任务栏闪烁 -----------------

try:
    if config['taskbar_flash']:
        from .winUtil import flash, stopFlash, show as show_window
        eManager.addListener('alarm.start', lambda data:flash(3, alarmLast, 500))
        eManager.addListener('alarm.stop', lambda data:stopFlash())
except ImportError as e:
    initUtil.warn(u'不支持任务栏闪烁。', e)
    flash = stopFlash = show_window = initUtil.doNothing

# 响铃超时延迟提醒
eManager.addListener('alarm.timeout', lambda data:manager.later(getNow() + alarmInterval))

# 停止响铃
eManager.addListener('alarm.stop', lambda data:player.play(None))
eManager.addListener('alarm.timeout', lambda data:player.play(None))

# 退出事件
quitEvent = threading.Event()
eManager.addListener('quit', lambda *args:quitEvent.set())


def mainLoop():
    # 初始化
    if config['warning_pause']:
        initUtil.warning_pause()
    eManager.clear()
    eManager.start()
    createIcon()
    listenThread.start()

    uiLoop = ReStartableThread(target=lambda stop_event:userInterface.mainLoop())
    uiLoop.start()

    # 阻塞等待退出事件
    logger.info('started')
    quitEvent.clear()
    quitEvent.wait()
    logger.info('begin quit')

    # 退出清理
    show_window(1)
    initUtil.reset()
    eManager.stop()
    deleteIcon()
    listenThread.stop(1)
    stopFlash()
    player.play(None)
    logger.info('exit')
