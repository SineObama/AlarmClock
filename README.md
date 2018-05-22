windows命令行闹钟，指令简单，带倒计时模式，可精确到秒。
可设置多个一次性闹钟、按星期重复的闹钟、按掉后一段时间（周期）再响的闹钟。
可自定义beep音频或使用本地铃声。任务栏闪烁提醒（需要win32包）。

运行：lib根目录下python -m sine.app.MultiAlarmClock


常用指令简介（v0.4-）

    添加一次性闹钟（可在空格后追加提示信息）：
    18:         晚上6点
    18:30       晚上6点半
    -10         倒计时10分钟
    -1:         倒计时1小时
    /10 12:     10号12点

    闹钟响后：
    回车        暂停闹钟，延迟响
    a           取消闹钟，不再响
    s           关闭闹钟

    w1 -10      把第一个闹钟改为10分钟之后



概念定义（v0.5-）

    一次性闹钟：用完自动删除。
    星期重复闹钟：一般意义上的闹钟。比如设置工作日响，也可不重复，表示只响一次（每天有效），之后自动关闭。
    周期重复闹钟：每次取消之后间隔一定时间后再响。和整点报时不同，是从取消之后计算。（本人用于提醒部分有冷却时间的游戏活动）

    取消闹钟（cancel）：“按掉”，表示完成任务或忽略。
    提醒闹钟（remind）：正在（响铃）提醒的闹钟。
    到期闹钟（expired）：提醒过的闹钟。



全部指令（v0.4-）

    分为三个页面

主页面（闹钟列表）：

    q ---- 退出

    添加闹钟：
    (日期) 时间 (信息) ---- 一次性闹钟
    (日期) 时间 w 星期 (信息) ---- 按星期重复
    (日期) 时间 r 周期 (信息) ---- 按周期重复

    修改：
    e序号 ---- 进入编辑页面
    w序号 (日期) 时间 ---- 修改时间
    a(序号) ---- 取消闹钟。默认取消第一个到期闹钟。
    s(序号) ... ---- 切换开关。默认关闭第一个到期闹钟，没有则对第一个闹钟生效。
    r序号 ... ---- 删除闹钟

    直接回车 ---- 延迟提醒，[提醒间隔]之后再响（对所有到期闹钟）
    
编辑页面：

    w(日期) 时间 ---- 修改时间
    a秒数 ---- 提前若干秒提醒
    m信息 ---- 修改信息
    r星期/周期 ---- 修改重复时间（闹钟种类不能更改）
    s(wav音频文件名) ---- 设置本地铃声，使用相对或绝对路径，可省略后缀名。此外，'default'表示播放beep音频；空表示无铃声；还可以用win32系统的几个注册表声音（见配置文件）。

响铃页面：

    直接回车 ---- 延迟提醒，[提醒间隔]之后再响（对所有提醒闹钟）
    a ---- 取消第一个提醒闹钟。
    s ---- 关掉第一个提醒闹钟。



指令参数格式（v0.4-）

    日期和时间（可配置）：

    默认时间格式：其中H小时，M分钟，S秒
    M
    H:
    :S
    H:M
    :M:S
    H:M:S

    默认日期格式：其中y两位年份，m月份，d日
    /d
    m/d
    y/m/d

    以'-'开始为倒计时模式，比如'-10'为10分钟之后。
    不推荐带日期的倒计时（目前实现是与1900/1/1相减得到时间差，语义比较奇怪）。


    周期：
    同'时间'格式，不能超过24小时。
    （也可以带日期，但同上不推荐，暂时也无法显示出来）。

    星期：
    星期一到日分别为1到7
    可以多个数字并列，无须按顺序
    比如"12345", "13756"
    也可输入"0"等表示不重复

    '...'表示可输入多个值。空格分离。



配置

    一般配置：
    clock.conf，里面有说明。

    日期时间：
    date.conf，time.conf中配置读取匹配格式（按顺序匹配）。
    文件内容为键值对：
    键为匹配读取数据的格式字符串；
    值为要替换的字段。主要针对闹钟时间的设置（正常模式），用于对未输入字段置0。
    （比如 %M=minute,second,microsecond 表示只读取匹配一个代表分钟的数字，并替换掉当前时间的分、秒、微秒，这就保留了当前时间的日期和小时，而没有读到的秒和微秒，相当于置0，最终实现在当前小时的这个分钟响铃。）

    beep音频配置：
    beep.conf配置调用winsound.Beep的时序。
    一行只有1个数字代表延迟（毫秒）。
    一行有逗号分隔的2个数字代表声音频率和时长（毫秒）。
    这段音频将会循环播放。

    注意：配置只在启动时读取，要生效必须重新启动。




更新日志：

v0.5.1, 2018-5-20
修复响铃自动停止时的异常问题。

v0.5.0, 2018-5-18
程序改由根目录以模块运行。
重新定义一次性闹钟，用完自动删除；原本的一次性闹钟改为星期重复闹钟，只是重复星期为空。
可以自定义beep音频。
配置中布尔变量可以用0设置（原本只能用False）。
修改了数据存储格式，提供了转换脚本。
闹钟列表中对非今天的闹钟以空行分隔。
电脑睡眠/待机（5分钟以上）唤醒后自动更新星期重复闹钟。
为了更新不影响配置，代码版本控制中，配置文件重新定义为默认配置文件，在无配置文件时将被复制。
修复部分异常警告没有生效。
修复配置读取异常时默认配置不生效。
修复不支持任务栏闪烁时导致的问题。
修复铃声文件不存在时的问题，会播放beep。
修复把目录视为文件判断为文件存在所导致的问题。
修复周期重复闹钟创建时的周期可为0。
修复提前提醒时间可为负。

v0.4.0, 2018-1-20
简化命令格式。
增加可编辑内容。
增加提前提醒功能。
可配置日期时间识别格式，还有其他配置。
更新数据文件版本为3。
列表增加“重复”的显示。
音频文件支持绝对或相对路径，并在启动程序或修改时检查存在性。

v0.3.5, 2018-1-18
增加配置：默认铃声（新增闹钟时）。使用'default'表示默认beep铃声。
同时，支持不响铃（设置为空）。

v0.3.4, 2018-1-12
部分配置从文件clock.conf读取，详细说明见配置文件。

v0.3.3
增加闹铃时任务栏闪烁的提醒
修正添加星期重复闹钟时没有进行过时判断

v0.3.2
修复添加星期重复时没有指定星期导致出错的问题。
修改时间时会对一次性和星期重复进行过时处理。

v0.3.1
一次性闹钟不会设置为过去时间了（比如当天过期则自动设置为明天）
过期一次性闹钟的开启改为“下一天”的时间
修复修改信息的问题（原本只会取信息第一个空格之前的内容）
补上编辑界面的指令错误提示

v0.3.0
增加自定义铃声的功能，要求wav格式放在根目录下
增加编辑页面，可供修改信息和铃声
调整页面信息的展示顺序
修复关闭普通闹钟后没有重新排序

v0.2.4
优化later：有提醒闹钟时延迟所有提醒闹钟，没有时延迟所有到期闹钟
修正cancel，对关闭的闹钟无效
优化switch：只在开启且过期才重置时间
优化闹钟排序方式：关闭的闹钟在最后（会按被关闭顺序）
更正expired为remind；对cancel和switch使用同样的选择方式：第一个提醒或过期
修正cf指令说明
说明中增加了概念解释

v0.2.3
修复闹铃自动结束不刷新界面（显示闹钟列表）的问题
修正回车说明
修复延迟提醒的逻辑错误
switch默认关闭首个到期闹钟
设置时间后自动开启闹钟
优化按键
取消remove的默认值

v0.2.2
修复错误指令的输出
增加修改时间
分离出2种时间输入方式：直接和倒计时，给所有输入情况

v0.2.1
修复暂停没有保存，启动30秒后不响的问题

v0.2
增加2种重复闹钟：星期、周期
增加闹钟的开关和停止操作
增加输入错误的反馈
响铃时间30秒

v0.1.1
增加修改信息
*修复删除输入不对时的重复反馈

v0.1
可添加指定(日期)时间的闹钟、倒计时闹钟，可附带信息；
到时间后，屏幕闪烁到期的闹钟，并有报警声；
手动暂停后，在闹钟列表中有!!!标识，5分钟后会再响
真正的关掉必须通过序号删除闹钟

倒计时只是输入形式，并不显示为倒计时
