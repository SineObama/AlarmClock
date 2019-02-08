# coding=utf-8
'''
“闹铃”播放器。可多次调用，前后值相同不会产生影响。
唯一接口: 
play(wav_filename)循环播放wav音频（不可为'default'）
play('default')播放windows beep声，可以在配置文件beep.conf设置样式（出现win7没有声音的问题，但在播放音乐时有声音，也可能是声卡问题）
play('')不作变化
play(None)停止
此外还可以用win32自带系统声音: 
'SystemAsterisk' Asterisk
'SystemExclamation' Exclamation
'SystemExit' Exit Windows
'SystemHand' Critical Stop
'SystemQuestion' Question
'SystemDefault'
'''

import os
import winsound
from sine.threads import ReStartableThread
from .exception import ClientException
from .globalData import data, useDefault, eManager

_list = []

def _init():
    def create_beep(Hz, last):
        def __func_bepp():
            winsound.Beep(Hz, last)
        return __func_bepp

    import time
    def create_sleep(last):
        def __func_sleep():
            time.sleep(last)
        return __func_sleep

    from .initUtil import warn
    from sine.properties import loadSingle, LineReader

    # 读入beep样式信息
    beep_filename = 'beep.properties'
    default_pattern = [(600,50),(200,),(600,50),(300,)]
    lines = []
    try:
        useDefault(data['location'], beep_filename)
        with open(beep_filename, 'r') as file:
            for line in LineReader(file):
                key, value = loadSingle(line)
                lines.append(key + value)
    except Exception as e:
        warn(u'从文件 %s 读取beep样式失败，将会使用默认值。' % (beep_filename), e)
        beep_pattern = default_pattern

    try:
        if 'beep_pattern' not in locals():
            beep_pattern = []
            for i, s in enumerate(lines):
                array = s.split(',')
                if len(array) > 1:
                    frequency = int(array[0].strip())
                    if (frequency < 37 or frequency > 32767):
                        raise ClientException(u'频率必须介于 37 与 32767 之间:', frequency)
                    duration = int(array[1].strip())
                    if (duration <= 0):
                        raise ClientException(u'持续时间必须为正:', duration)
                    if (duration > 2000):
                        raise ClientException(u'持续时间过长（大于2000毫秒）:', duration)
                    beep_pattern.append((frequency, duration))
                else:
                    last = int(array[0].strip())
                    if (last <= 0):
                        raise ClientException(u'间隔时间必须为正:', last)
                    beep_pattern.append((last,))
    except Exception as e:
        warn(u'读取beep样式失败，将会使用默认值。', e)
        beep_pattern = default_pattern

    for s in beep_pattern:
        if len(s) > 1:
            _list.append(create_beep(s[0], s[1]))
        else:
            _list.append(create_sleep(s[0] / 1000.0))

_init()

def _alarm(stop_event):
    while 1:
        for func in _list:
            if stop_event.is_set():
                return
            func()
    return

_name = None # 保存当前播放的内容，字符串，必然非空''
_expect = None # 静音时保存期望播放的内容
_beep = 'default'
_alarmThread = ReStartableThread(target=_alarm)

def play(name):
    '''静音时保存期望播放的内容，并把参数当做None以实现停止播放'''
    global _name
    if not data['sound']:
        _expect = name
        name = None
    if _name == name or name == '':
        return
    if _name != None: # 正在播则停止当前beep或者音乐
        _alarmThread.stop(1)
        winsound.PlaySound(None, winsound.SND_PURGE)
    if name != None:
        if name == _beep:
            _alarmThread.start()
        else:
            # 播放wav音频，或者系统声音
            if os.path.isfile(name):
                winsound.PlaySound(name, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            elif os.path.isfile(name + '.wav'):
                winsound.PlaySound(name + '.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            elif name in _extraLegal:
                winsound.PlaySound(name, winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
    _name = name
    return

_extraLegal = [
'',
_beep,
'SystemAsterisk',
'SystemExclamation',
'SystemExit',
'SystemHand',
'SystemQuestion',
'SystemDefault']

def isLegal(name):
    '''检查音频文件是否存在或为以上合法系统值。'''
    if name in _extraLegal:
        return True
    if os.path.isfile(name):
        return True
    if os.path.isfile(name + '.wav'):
        return True
    return False

def assertLegal(name):
    if not isLegal(name):
        raise ClientException(u'波形文件 \'%s\' 或者 \'%s.wav\' 不存在（也不是系统声音）。' % (name, name))

def _handleSoundChange(unused):
    if data['sound']:
        play(_expect)
    else:
        play(None)

eManager.addListener('sound.change', _handleSoundChange)
