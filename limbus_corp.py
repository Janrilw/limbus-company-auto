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
import asyncio


class Widget_LCB(Widget):
    def __init__(self, tag, father: Panel):
        super().__init__(tag, "img_lcb\\%s.bmp" % tag, father)


class LimbusCorp(Game):
    def do_frame(self):
        self.get_img()
        self.update_ptr()
        if not p2.is_current():
            self.to(p2)

    def frame_func(self):
        self.do_frame()


g = LimbusCorp('LimbusCompany', 0.5)

p1 = Panel('p1', g)

p2 = Panel('p2', g)

w3 = Widget_LCB('w3', p1)
p1.s(w3).is_the_way_to(p2)
w3p = Widget_LCB('w3p', p2)

g.frame_func()
