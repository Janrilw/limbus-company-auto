# Autogame 边狱巴士自动化

## 简介
* 刷镜之地牢真的太坐牢，所以尝试了一下自动化。
* 这个自动化只适配电脑steam端，**且脚本运行时你不能干别的事情**。
* 目前的版本能比较稳定地自动化，但也可能跑着跑着卡壳了。代码会随着时间逐渐完善，也欢迎大家来提pr。
* 在很久以前在网上找了图像识别方面的代码，改到能用之后放在这里，即baseImage和image_registration两个模块。如有侵权请联系删除。


## 注意
**无法保证滥用此脚本带来的封号风险！** 请在正常范围内使用！

## 使用方法
时间有限，在此简要列出使用方法。


操作步骤：
0. 这个步骤对于完全不懂python的小白可能需要一定时间来研究。
1. 下载 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 并安装。（其完整版Anaconda过于庞大，推荐此精简版，也不容易出现散装python的情况）
2. 按Windows+S搜索`Miniconda3 Prompt`，并右键以管理员模式启动。
3. 用conda或者pip安装opencv、pywin32、pyautogui、numpy这几个模块，如果pip还不行那就百度“pip清华镜像源”。安装模块的代码是`conda install opencv`或者`pip install opencv`，我也不记得拿哪个装的了，装不起来的话两个都试试。要是装起来还是头大，那就装个完整版Anaconda，然后打开Anaconda Navigator，有图形化界面装起来舒服一些。也许运行的时候还会报错，说少了什么模块，一般少什么装什么就好。
4. 进入游戏，登录进入主界面，放着不动。
5. 用cd指令跳转到本仓库目录，输入`python limbus_corp.py`运行脚本。

如果用pycharm运行也**必须用管理员模式启动**。

## 偏好人格和ego
`img_lcb`文件夹存放了所有UI标志图片，可以自行截图替换。
`sinner_pre`开头的是自选人格。
`ego_pre`开头的是自选ego。

如果一个罪人有多个ego，那么同名的文件后依次追加下划线，这样会被程序认定为一组文件。如`ego_pre9`、`ego_pre9_`和`ego_pre9__`被视作一组文件。


## 文件结构
* recognition：图像识别方面的代码
* screenshot：截图用的
* mouse：尝试鼠标操作
* base：基本结构，通用功能，目的是让别的游戏也可以复用
* limbus_corp：用来记录游戏UI框架和自动化逻辑

