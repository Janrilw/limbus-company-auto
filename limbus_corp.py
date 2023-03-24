#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" ================================
limbus_corp.py
边狱巴士相关定义
info:

- time: 2023/3/23 9:29
- author: 云绝万里
- email: janrilw@163.com
"""
import time

import win32con
import win32gui

from base import Game, Panel, Widget

g = Game('LimbusCompany', 0.5)

p1 = Panel(g)
p2 = Panel(g)
w1p = Widget('img_lcb/w1p.jpg', p1)
w2 = Widget('img_lcb/w2.jpg', p1)
w1 = Widget('img_lcb/w1.jpg', p2)
w2p = Widget('img_lcb/w2p.jpg', p2)
g.register_vertex('w1', p1)
g.register_vertex('w2', p2)
g.frame_func()

