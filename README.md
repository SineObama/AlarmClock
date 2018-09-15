# 闹钟

windows命令行闹钟，指令简单，带倒计时模式，可精确到秒。  
可设置多个一次性闹钟、按星期重复的闹钟、按掉后一段时间（周期）再响的闹钟。  
可自定义beep音频或使用本地铃声。任务栏闪烁提醒（需要win32包）。

*此为PyPI库，依赖另一些PyPI上的（本人的）库，建议用pip安装*

# 从PyPI安装

`pip install sine.alarmclock`

# 运行

选择一个工作目录，命令行执行：

`python -m sine.alarmclock`

该工作目录用于：
* 保存闹钟数据
* 保存用户配置  
* 放置本地铃声（方便引用）



# 常用指令简介（v0.4-）

假设当前时间5月8日17:10

    添加一次性闹钟（可追加提示信息）：
    18:         18:00
    18:30       18:30
    30          17:30
    -10         17:20 （10分钟后）
    -1:         18:10 （1小时后）
    /10 12:     5月10号12:00

    闹钟响后：
    Enter       暂停闹钟，延迟响
    a           取消闹钟，不再响
    s           关闭闹钟

    w1 -10      把第一个闹钟改为10分钟后



# 概念定义（v0.5-）

一次性闹钟
: 用完自动删除。

星期重复闹钟
: 一般意义上的闹钟。比如设置工作日响，也可不重复，表示只响一次（每天有效），之后自动关闭。

周期重复闹钟
: 每次取消之后间隔一定时间后再响。和整点报时不同，是从取消之后计算。（本人用于提醒部分有冷却时间的游戏活动）

取消闹钟（cancel）
: “按掉”，表示完成任务或忽略。

提醒闹钟（remind）
: 正在（响铃）提醒的闹钟。

到期闹钟（expired）
: 提醒过的闹钟。



# 全部指令（v0.4-）

分为三个页面

### 主页面（闹钟列表）：

    q ---- 退出

    添加闹钟：
    [<date>] <time> [<msg>]              ---- 一次性闹钟
    [<date>] <time> w <weekdays> [<msg>] ---- 按星期重复
    [<date>] <time> r <period> [<msg>]   ---- 按周期重复

    修改：
    e<index>                 ---- 进入编辑页面
    w<index> [<date>] <time> ---- 修改时间
    a[<index>]               ---- 取消闹钟。默认取消第一个到期闹钟。
    s[<index> ...]           ---- 切换开关。默认关闭第一个到期闹钟或第一个闹钟。
    r<index> ...             ---- 删除闹钟

    Enter ---- 延迟提醒，{提醒间隔}之后再响（对所有到期闹钟）

### 编辑页面：

    w[<date>] <time>       ---- 修改时间
    a<seconds>             ---- 提前若干秒提醒
    m<msg>                 ---- 修改信息
    r[<weekdays>|<period>] ---- 修改重复时间（闹钟种类不能更改）
    s[<wav_file>]          ---- 设置本地铃声，使用相对或绝对路径，可省略后缀。
                                此外，'default'表示播放beep音频；空表示无铃声；
                                还可用win32的几个注册表声音（见配置文件）。

### 响铃页面（屏幕闪烁时）：

    Enter ---- 延迟提醒，{提醒间隔}之后再响（对所有提醒闹钟）
    a     ---- 取消第一个提醒闹钟。
    s     ---- 关掉第一个提醒闹钟。



# 指令参数格式（v0.4-）

### 日期和时间（date/time）

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

时间前面加上'-'为倒计时模式，比如'-10'为10分钟之后。  


### 周期（period）

同'时间'格式，不能超过24小时。  

### 星期（weekdays）

* 星期一到日分别对应 1234567
* 数字并列，可乱序
* 只输入"0"等其他字符表示不重复

比如"12345", "13756", "0"


### 其他

'...'表示可输入多个值（空格分离）。



# 其他特性

* 列表中显示的时间为闹钟下一次生效的时间，类似于日程或事件。
* 列表在非当天的闹钟之前添加一个空行，突出今天的闹钟（任务或事件）。
* **可取消未到期的闹钟**：
    * 对星期重复闹钟，可取消下一次提醒。  
    例如当前星期日，闹钟在工作日，取消一次则星期一不会响铃，时间相应推迟到星期二，以此类推。  
    特别地，对不重复的闹钟，关闭。
    （通过重新开启闹钟重置。）
    * 对周期重复闹钟，从当前时间重新开始计时。（类似于响铃后取消。）
    * 对一次性闹钟，相当于关闭。
* 星期重复闹钟，类似一般意义上的闹钟，会在程序重新启动（包括电脑唤醒后）刷新。  
表现类似于手机闹钟，关机后到时的闹钟不会在开机后补充响铃。
* 添加闹钟时，如果闹钟时间已过，则自动推迟设置为明天（对于星期重复闹钟则是下一个有效日）。


# 配置

##### 一般配置

clock.conf，里面有说明。

##### 日期时间格式

date.conf，time.conf中配置读取匹配格式（按顺序匹配）。  
文件内容为键值对：
* key：匹配读取数据的格式字符串；  
* value：要替换的字段。主要针对闹钟时间的设置（正常模式），对未输入字段置0。  

原理说明：比如 `%M=minute,second,microsecond` 只读取一个数字（分钟），  
替换掉当前时间的分、秒、微秒，这就保留了当前时间的日期和小时，  
而没有读到的秒和微秒，相当于置0，最终设置为当前小时的这个分钟。  

##### beep音频配置

beep.conf配置调用winsound.Beep的时序。  
每行有2种格式：
* 只有1个数字代表延迟（毫秒）。  
* 逗号分隔的2个数字代表声音频率和时长（毫秒）。  
这段音频将会循环播放。  

*配置只在启动时读取，要生效必须重新启动。*

##### 托盘图标

使用ico后缀格式的图片文件：
正常状态clock.ico
静音状态quiet.ico
提醒状态alarm.ico
需要自定义时替换相应文件即可。




# 更新日志

#### v0.6.1, 2018-9-15

* 托盘右键可以取消响过的闹钟。
* 增加不支持托盘时的处理。
* 修复启动时悬浮不显示闹钟的问题。

#### v0.6.0, 2018-9-12
* **增加托盘图标的显示与功能:**
* 单击图标隐藏/显示窗口。
* 图标右键菜单：延迟提醒、静音、退出。
* 有到期闹钟时图标闪烁。
* 悬停显示到期闹钟或当日闹钟。

#### v0.5.7, 2018-8-13

* 修改时间时也会将以过时间推迟到明天。

#### v0.5.6, 2018-7-30

* 修复添加星期闹钟时会在当天响的问题。
* *凌晨刷新列表。*

#### v0.5.5, 2018-6-7

* **更改配置文件格式为properties**（使用新的properties库读取）。  
    更新了时间格式文件（time）配置，  
    为了适配properties格式对冒号进行了转义，  
    另外可用小数点代替冒号。  
* 指令接受大写字母
* 修复v0.5.2以来项目没有上传默认配置文件到PyPI。
* 优化任务栏闪烁，同时闪烁窗口。（flashWindow库更新）

#### v0.5.4, 2018-6-4

修复5.0版本后开启时没有重排序的问题。  

#### v0.5.3, 2018-6-4

主列表的空行也会间隔开已关闭的闹钟了。  

#### v0.5.2, 2018-5-23

项目管理调整：项目改成独立库，发布到PyPI。  
从github的个人python仓库独立出来作为一个项目，以PyPI库的格式管理，同时将几个依赖移至PyPI，以便通过pip安装。  

#### v0.5.1, 2018-5-20

修复响铃自动停止时的异常问题。  

#### v0.5.0, 2018-5-18

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

#### v0.4.0, 2018-1-20

简化命令格式。  
增加可编辑内容。  
增加提前提醒功能。  
可配置日期时间识别格式，还有其他配置。  
更新数据文件版本为3。  
列表增加“重复”的显示。  
音频文件支持绝对或相对路径，并在启动程序或修改时检查存在性。  

#### v0.3.5, 2018-1-18

增加配置：默认铃声（新增闹钟时）。使用'default'表示默认beep铃声。  
同时，支持不响铃（设置为空）。  

#### v0.3.4, 2018-1-12

部分配置从文件clock.conf读取，详细说明见配置文件。  

#### v0.3.3

增加闹铃时任务栏闪烁的提醒  
修正添加星期重复闹钟时没有进行过时判断  

#### v0.3.2

修复添加星期重复时没有指定星期导致出错的问题。  
修改时间时会对一次性和星期重复进行过时处理。  

#### v0.3.1

一次性闹钟不会设置为过去时间了（比如当天过期则自动设置为明天）  
过期一次性闹钟的开启改为“下一天”的时间  
修复修改信息的问题（原本只会取信息第一个空格之前的内容）  
补上编辑界面的指令错误提示  

#### v0.3.0

增加自定义铃声的功能，要求wav格式放在根目录下  
增加编辑页面，可供修改信息和铃声  
调整页面信息的展示顺序  
修复关闭普通闹钟后没有重新排序  

#### v0.2.4

优化later：有提醒闹钟时延迟所有提醒闹钟，没有时延迟所有到期闹钟  
修正cancel，对关闭的闹钟无效  
优化switch：只在开启且过期才重置时间  
优化闹钟排序方式：关闭的闹钟在最后（会按被关闭顺序）  
更正expired为remind；对cancel和switch使用同样的选择方式：第一个提醒或过期  
修正cf指令说明  
说明中增加了概念解释  

#### v0.2.3

修复闹铃自动结束不刷新界面（显示闹钟列表）的问题  
修正回车说明  
修复延迟提醒的逻辑错误  
switch默认关闭首个到期闹钟  
设置时间后自动开启闹钟  
优化按键  
取消remove的默认值  

#### v0.2.2

修复错误指令的输出  
增加修改时间  
分离出2种时间输入方式：直接和倒计时，给所有输入情况  

#### v0.2.1

修复暂停没有保存，启动30秒后不响的问题  

#### v0.2

增加2种重复闹钟：星期、周期  
增加闹钟的开关和停止操作  
增加输入错误的反馈  
响铃时间30秒  

#### v0.1.1

增加修改信息  
修复删除输入不对时的重复反馈  

#### v0.1

可添加指定(日期)时间的闹钟、倒计时闹钟，可附带信息；  
到时间后，屏幕闪烁到期的闹钟，并有报警声；  
手动暂停后，在闹钟列表中有!!!标识，5分钟后会再响  
真正的关掉必须通过序号删除闹钟  

倒计时只是输入形式，并不显示为倒计时  
