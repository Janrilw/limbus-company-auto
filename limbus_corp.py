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
import os.path
import time

from base import Game, Panel, Widget
from baseImage import Image


class Widget_LCB(Widget):
    state = 1  # 指代当前为第几个状态

    def __init__(self, tag, path=None, father: Panel = None):
        if os.path.exists("img_lcb\\%s_.bmp" % tag):
            tags = []
            cur = 0
            while os.path.exists("img_lcb\\%s%s.bmp" % (tag, "_" * cur)):
                tags.append(tag + "_" * cur)
                cur += 1
            tag = tags
            print('multi tag:', tags)
        if type(tag) != str:
            self.tags = tag
            self.pathes = ["img_lcb\\%s.bmp" % t for t in tag]
            self.imgs = [Image(p) for p in self.pathes]
            tag = tag[0]
        else:
            self.tags = None
        super().__init__(tag, "img_lcb\\%s.bmp" % (path or tag), father)

    def check_existence(self):
        if self.tags is None:
            return super(Widget_LCB, self).check_existence()
        else:
            for i, p in enumerate(self.imgs):
                self.img = p
                p1, p2, p3 = super(Widget_LCB, self).check_existence()
                if p1 is not None:
                    self.state = i + 1
                    print('state switch to', i + 1, p3)
                    return p1, p2, p3


class LimbusCorp(Game):

    def mirror_dungeon(self):
        # w_mir_char_conf.check_existence()
        self.wait()
        self.update_ptr()
        self.select_ego_gift()
        self.select_sinner()

        pass

    def select_sinner(self):
        print('select_sinner')
        prefer = [12, 5, 6, 8, 2]
        self.get_img()
        if p_mir_char_chs.is_current():
            for v in prefer:
                w_chars[v - 1].click()
            cur = 1
            self.get_img()
            w_mir_char_conf.check_existence()
            while w_mir_char_conf.state != 2:
                if cur not in prefer:
                    w_chars[cur - 1].click()
                cur += 1
                if cur == 12:
                    break
            w_mir_char_conf.click()

    def select_ego_gift(self):
        self.get_img()
        if p_mir_ego_chs.is_current():
            w_ego_frame.click()
            w_ego_conf.click()
        pass

    def do_frame(self):
        # self.to(p_mirror1_conf)
        # w_mirror1_conf.click()
        self.mirror_dungeon()

        return True

    def frame_func(self):
        self.get_img()
        self.update_ptr()
        self.do_frame()


game = LimbusCorp('LimbusCompany', 0.75)

p_main = Panel('非第三个主界面')
w3 = Widget_LCB('ui_w3')

p_main3 = Panel('第三个主界面')
w3.is_the_way_to(p_main3)
w3p = Widget_LCB('ui_w3p')
w_mirror_enter = Widget_LCB('ui_mirror_enter')

p_mirror_chs = Panel('镜牢选择')
w_mirror_enter.is_the_way_to(p_mirror_chs)
w_dung1 = Widget_LCB('ui_dung1')

p_mirror1_conf = Panel('镜牢1确认')
w_dung1.is_the_way_to(p_mirror1_conf)
w_mirror1_conf = Widget_LCB('ui_conf')

p_mir_ego_chs = Panel('镜牢ego选择')
w_mirror1_conf.is_the_way_to(p_mir_ego_chs)
w_ego_frame = Widget_LCB('ego_frame')
w_ego_conf = Widget_LCB('ego_conf')

p_mir_char_chs = Panel('镜牢罪人选择')
w_chars = [Widget_LCB('sinner%d' % i) for i in range(1, 13)]
w_mir_char_conf = Widget_LCB('sinner_conf')

p_mir_id_chs1 = Panel('镜牢罪人人格选择1')
w_id_sel1 = Widget_LCB('id_sel')

game.frame_func()
