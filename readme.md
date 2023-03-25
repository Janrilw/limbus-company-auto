# Autogame 边狱巴士自动化

## 简介
刷镜牢太坐牢，所以尝试了一下自动化。

这个自动化只适配电脑steam端，且脚本运行时你不能干别的事情。

目前的版本只能半自动化，可能跑着跑着卡壳了。代码会随着时间逐渐完善，也欢迎大家来提pr。

在很久以前在网上找了图像识别方面的代码，改到能用之后放在这里，即baseImage和image_registration两个模块。如有侵权请联系删除。


## 使用方法
因为时间有限，在此简要列出使用方法。
对于熟练使用者，直接用仓库自带的environment.yaml构建新环境，再在pycharm里跑就行。但是pycharm**必须用管理员模式启动**，游戏本体似乎用了一些手段来屏蔽非人工操作。

完整步骤：

1. 下载 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 并安装。（其完整版Anaconda过于庞大，推荐此精简版）
2. 以管理员模式运行Miniconda3 Prompt，并用指令`conda env create -f environment.yaml`创建python虚拟环境。（注意用cd指令切换到仓库所在目录） 参考 [conda使用之.yaml文件环境配置文件用于新设备部署环境 - 知乎](https://zhuanlan.zhihu.com/p/586560032) 。
4. 进入游戏，登录进入主界面，放着不动。
3. 使用指令`conda activate autogame` 激活虚拟环境，注意用cd指令切换到仓库所在目录，然后用指令`python limbus_corp.py`运行自动化脚本。游戏能自动切换过去。





## 文件结构
* recognition：图像识别方面的代码
* screenshot：截图用的
* mouse：尝试鼠标操作
* base：基本结构，通用功能，目的是让别的游戏也可以复用
* limbus_corp：用来记录游戏UI框架和自动化逻辑

