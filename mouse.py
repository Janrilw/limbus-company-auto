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
import math
import time

import pymouse
from pymouse.windows import PyMouse
import pyautogui as pi
import win32api


def click(x, y):
    print('clicked', x, y)
    pi.moveTo(x, y, duration=0.1)
    # time.sleep(.7)
    pi.click()
    # win32api.SetCursorPos((x,y))


def move(x, y):
    pi.moveTo(x, y, duration=0.1)


if __name__ == '__main__':
    m = PyMouse()

    print(m.screen_size())
    time.sleep(2)
    m.click(1652, 1123)

    for i in range(10):
        print(m.position())
        click(int(1250 + math.cos(i / 10) * 100), 1250)
        # m.click(int(1250 + math.cos(i / 10) * 100), 1250)
        time.sleep(0.1)

    # for i in range(1000):
    #     # m.click(int(1250+math.cos(i/10)*100),1250)
    #     print("\r%s" % str(m.position()), end='')
    #     time.sleep(0.01)
