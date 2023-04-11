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
# import math
# import time

# import pymouse
# from pymouse.windows import PyMouse
import math
import random
import time

import pyautogui as pi
# import win32api
from multiprocessing import Process


def click(x, y):
    print('clicked', x, y)
    pi.moveTo(x, y, duration=0.25, _pause=False)
    # time.sleep(.7)
    pi.click()
    # win32api.SetCursorPos((x,y))


def move(x, y):
    pi.moveTo(x, y, duration=0.25, _pause=False)


def _sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def scroll(n=10):
    for _ in range(abs(n)):
        pi.scroll(10 * _sign(n))
        # time.sleep(0.05)


def random_move():
    print(222)
    for i in range(100):
        pi.moveRel(2 * math.cos(i / 100 * 2*math.pi), 2 * math.sin(i / 100 * 2*math.pi), _pause=False)
        time.sleep(0.016)

    pass


drag = pi.drag

if __name__ == '__main__':
    p = Process(target=random_move)
    p.start()
    print(111)

    pass
    # m.click(1652, 1123)
    #
    # for i in range(10):
    #     print(m.position())
    #     click(int(1250 + math.cos(i / 10) * 100), 1250)
    #     # m.click(int(1250 + math.cos(i / 10) * 100), 1250)
    #     time.sleep(0.1)

    # for i in range(1000):
    #     # m.click(int(1250+math.cos(i/10)*100),1250)
    #     print("\r%s" % str(m.position()), end='')
    #     time.sleep(0.01)
