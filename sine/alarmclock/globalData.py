# coding=utf-8
'''
全局数据。包括配置的读取和验证。
对于缺少的配置赋予默认值并暂停警告。
'''

import os.path as spath
import shutil
from . import mylogging
from sine.utils import EventManager
from .__meta__ import VERSION as version

clocks = []
data = {}
config = {}
timeFormats = []
dateFormats = []
eManager = EventManager(mylogging.getLogger(mylogging.rootPath + '.eManager'))
title = u'闹钟 v' + version

def _init():
    import sys
    from sine.utils.properties import load, loadSingle, LineReader
    from sine.utils import Path
    from .initUtil import warn

    def boolConverter(s):
        '''对空或者0开头的字符串视为False，其余视为True'''
        if s == '' or s.startswith('0'):
            return False
        return True

    # 获取代码文件所在目录（保存了默认的配置文件等）
    location = Path(__file__).join('..')
    data['location'] = location


    # 读入配置 ---------------

    conf_filename = 'clock.properties'
    allMiss = False
    try:
        useDefault(location, conf_filename)
        with open(conf_filename, 'r', encoding='latin') as file:
            config.update(load(file))
    except Exception as e:
        warn(u'从 %s 文件加载配置失败，将会使用默认配置。' % (conf_filename), e)
        allMiss = True

    # 猜测编码为utf8或gbk（简单对比转换出错率），并解码
    utf8_error = 0
    for k, v in config.items():
        v = v.encode('latin')
        try:
            v.decode('utf8')
        except Exception as e:
            utf8_error += 1
    gbk_error = 0
    for k, v in config.items():
        v = v.encode('latin')
        try:
            v.decode('gbk')
        except Exception as e:
            gbk_error += 1
    # 优先猜测为utf8
    if utf8_error <= gbk_error:
        encoding = 'utf8'
    else:
        encoding = 'gbk'
    if utf8_error > 0 and gbk_error > 0:
        warn(u'无法用UTF-8或GBK解码配置文件 %s ，配置的值会部分丢失且可能有异常。' % (conf_filename))
    # 解码
    for k, v in config.items():
        try:
            config[k] = v.encode('latin').decode(encoding)
        except Exception as e:
            pass

    # 为缺失值填充默认配置(键, 默认值, 转换器)
    default_config = [
    ('warning_pause', True, boolConverter),
    ('sound', True, boolConverter),
    ('show_msg', True, boolConverter),
    ('taskbar_flash', True, boolConverter),
    ('screen_flash_mode', '0111101111', None),
    ('alarm_last', 30, int),
    ('alarm_interval', 300, int),
    ('default_remindAhead', 60, int),
    ('default_sound', 'default', None),
    ('format', '%Y-%m-%d %H:%M:%S %%warn %%3idx %%3state %%msg', None),
    ('flash_format', '%Y-%m-%d %H:%M:%S %%msg', None),
    ('warn', '!!!', None),
    ('state.ON', 'ON', None),
    ('state.OFF', 'OFF', None),
    ('datafile', 'clocks.txt', None),
    ('encoding', 'utf-8', None),
    ('debug', False, boolConverter),
    ('debug.no_clear_screen', False, boolConverter),
    ]

    if allMiss:
        for (key, default, converter) in default_config:
            config[key] = default
    else:
        for (key, default, converter) in default_config:
            if key not in config:
                warn(u'找不到设置\'%s\'，将会使用默认值\'%s\'。' % (key, str(default)))
                config[key] = default
            elif converter:
                try:
                    config[key] = converter(config[key])
                except Exception as e:
                    warn(u'读取\'%s=%s\'异常，将会使用默认值\'%s\'。' % (key, str(config[key]), str(default)), e)
                    config[key] = default

    # 从默认值载入或应用状态
    data['sound'] = config['sound']
    data['show_msg'] = config['show_msg']
    mylogging.setDebug(config['debug'])


    # 读入日期和时间识别格式配置 --------------

    format_filename = 'time.properties'
    try:
        useDefault(location, format_filename)
        formats = []
        with open(format_filename, 'r', encoding='latin') as file:
            for line in LineReader(file):
                key, value = loadSingle(line)
                formats.append((key, value.split(',')))
    except Exception as e:
        warn(u'从 %s 文件读取时间识别格式出错，将会使用默认格式。' % (format_filename), e)
        formats = [(   '%M'   ,        ['minute', 'second', 'microsecond']),
                  ('%H:'     ,['hour', 'minute', 'second', 'microsecond']),
                  ('%H.'     ,['hour', 'minute', 'second', 'microsecond']),
                  (     ':%S',                  ['second', 'microsecond']),
                  (     '.%S',                  ['second', 'microsecond']),
                  ('%H:%M'   ,['hour', 'minute', 'second', 'microsecond']),
                  ('%H.%M'   ,['hour', 'minute', 'second', 'microsecond']),
                  (  ':%M:%S',        ['minute', 'second', 'microsecond']),
                  (  '.%M.%S',        ['minute', 'second', 'microsecond']),
                  ('%H:%M:%S',['hour', 'minute', 'second', 'microsecond']),
                  ('%H.%M.%S',['hour', 'minute', 'second', 'microsecond'])]
    timeFormats.extend(formats)

    format_filename = 'date.properties'
    try:
        useDefault(location, format_filename)
        formats = []
        with open(format_filename, 'r', encoding='latin') as file:
            for line in LineReader(file):
                key, value = loadSingle(line)
                formats.append((key, value.split(',')))
    except Exception as e:
        warn(u'从 %s 文件读取日期识别格式出错，将会使用默认格式。' % (format_filename), e)
        formats = [(     '/%d',                 ['day']),
                  (   '%m/%d',        ['month', 'day']),
                  ('%y/%m/%d',['year', 'month', 'day'])]
    dateFormats.extend(formats)


def useDefault(location, filename):
    '''配置文件 filename 不存在时从 location 复制默认文件。'''
    suffix = '.default'
    filepath = filename
    if not spath.isfile(filepath):
        defaultpath = location.join(filename + suffix)
        if spath.isfile(defaultpath):
            shutil.copyfile(defaultpath, filepath)

_init()
