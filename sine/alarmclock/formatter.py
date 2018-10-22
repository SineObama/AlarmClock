# coding=utf-8
'''
为闹钟格式化输出的字符串。
根据指定格式，创建对象进行格式化。
格式说明：
先填充闹钟里的时间，使用 datetime 函数 strftime ，故匹配如 '%Y-%m-%d %H:%M:%S' 的格式。
自定义字段格式如 '%%3warn' 其中 3 的位置可使用的参数等同于一般的格式化，而 warn 是自定义标识。
自定义字段使用2个百分号，填充时间时被转换为单个百分比，如 '%3warn'。
再填充自定义字段时，用正则表达式进行匹配，分别把自定义标识替换为对应的数据类型标识，如 '%3s' ，再进行一般的格式化。
'''

class Str(object):
    '''保存半成品的字符串'''
    import re as _re
    def __init__(self, s=''):
        self._s = s
        return
    def fill(self, t, t2, o):
        '''填充。 t 是自定义标识， t2 为目标数据类型标识。 o 是填充内容。'''
        ss = self._re.findall(r'%[^%]*(?='+t+')', self._s)
        for s in ss:
            self._s = self._s.replace(s+t, (s+t2) % (o), 1)
        return self._s

def create(config, format):
    '''根据配置创建对象，避免每次都传入配置。'''
    warn = config['warn']
    on = config['state.ON']
    off = config['state.OFF']
    def formatter(i, clock):
        s = Str(clock['time'].strftime(format))
        s.fill('warn', 's', warn if clock.isExpired() else '')
        s.fill('idx', 'd', i)
        s.fill('state', 's', on if clock['on'] else off)
        s.fill('msg', 's', clock['msg'])
        return s.fill('rep', 's', clock.repeatStr())
    return formatter
