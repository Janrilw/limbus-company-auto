#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" ================================
mouse.py
尝试py鼠标模块
info:

- time: 2023/3/24 14:17
- author: 云绝万里
- email: janrilw@163.com
"""

import time

import pymouse
from pymouse.windows import PyMouse

m = PyMouse()
print(m.screen_size())
for i in range(1000):
    print("\r%s" % str(m.position()), end='')
    time.sleep(0.01)
