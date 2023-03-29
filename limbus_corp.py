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
from __future__ import annotations

import os.path
import random
import time

import mouse
import pyautogui as pi

from base import Game, Panel, Widget
from baseImage import Image, Rect


class Widget_Auto(Widget):
    """附着在panel上的widget，判断panel是否为当前时会自动遍历自身的widget来判断"""
    state = 1  # 指代当前为第几个状态

    def __init__(self, tag, path=None, father: Panel | bool = None):
        if type(tag) == str and os.path.exists("img_lcb\\%s_.bmp" % tag):
            tags = []
            cur = 0
            while os.path.exists("img_lcb\\%s%s.bmp" % (tag, "_" * cur)):
                tags.append(tag + "_" * cur)
                cur += 1
            tag = tags
        if type(tag) != str:
            self.tags = tag
            self.pathes = ["img_lcb\\%s.bmp" % t for t in tag]
            self.imgs = [Image(p) for p in self.pathes]
            print('multi tag:', tag)
            tag = tag[0]
        else:
            self.tags = None
        super().__init__(tag, "img_lcb\\%s.bmp" % (path or tag), father)

    def check_existence(self, auto_fetch=False, limit: Rect = None, forbid=None):
        if auto_fetch:
            self.father.father.get_img()
        if self.tags is None:
            return super(Widget_Auto, self).check_existence(limit=limit, forbid=forbid)
        else:
            for i, p in enumerate(self.imgs):
                self.img = p
                p1, p2, p3 = super(Widget_Auto, self).check_existence(limit=limit, forbid=forbid)
                if p3 != 0:
                    self.state = i + 1
                    print('state switch to', i + 1, p3)
                    return p1, p2, p3
            return 0, 0, 0


class Widget_Simple(Widget_Auto):
    """无附着的控件，可以直接当一个图片来click和check"""
    def __init__(self, tag, path=None):
        super(Widget_Simple, self).__init__(tag, path, father=False)


class NODE:
    battle = 1
    event = 2
    fin = 3


class Event(Widget_Simple):
    def __init__(self, tag, default_act):
        super().__init__(tag)
        self.default_act = default_act
        self.task = None

    def do(self):
        w_mir_event_skip.click()
        self.father.father.wait(2)
        w_mir_event_skip.click()
        self.father.father.wait(2)
        if self.task:
            pass
        else:
            w_mir_event_btn.click_by_index(self.default_act - 1)
            w_mir_event_skip.click()
            self.father.father.wait()
            w_mir_event_skip.click()
            self.father.father.wait()
            w_mir_event_con.click()
            pass
        self.father.father.wait()
        if self.tag == 'event1':
            self.father.father.upgrade_id()



events = [Event('event%d' % i, 1) for i in range(1, 2)]
events.append(Event('event0', 1))


class LimbusCorp(Game):
    # def __init__(self, *args, **kwargs):
    #     super(LimbusCorp, self).__init__(*args, **kwargs)

    def wait_for_load(self):
        self.wait(2)
        count = 0
        while True:
            r = loading.check_existence(auto_fetch=True)
            count += 1
            if r[0] == 0:
                if count < 3:
                    count += 1
                    continue
                break
            else:
                self.wait(2)

    def wait_for_connect(self):
        self.wait(2)
        count = 0
        while True:
            r = connecting.check_existence(auto_fetch=True)
            if r[0] == 0:
                if retry.click():
                    continue

                if count < 2:
                    count += 1
                    continue
                print('ignore connect')
                break
            else:
                print('wait 5')
                self.wait(5)
                retry.click()

    def wait_for_panel(self, panel):
        print('wait for panel', panel.tag)
        count = 0
        while not panel.is_current():
            # print(panel.is_current())
            if count > 5:
                break
            count += 1
            self.wait()

    def mirror_dungeon(self):
        # w_mir_char_conf.check_existence()
        self.floor = 1
        self.wait()
        self.update_ptr()
        self.wait_for_connect()

        self.select_ego_gift()
        self.select_sinner()
        self.select_id()
        self.wait_for_connect()

        while True:
            self.get_img()
            conf.click()
            conf2.click()
            node = self.select_node()
            # node=NODE.battle
            if node == NODE.battle:
                # self.wait_for_connect()
                # self.wait_for_load()
                self.battle()
            elif node == NODE.event:
                self.wait()
                self.get_img()
                for e in events:
                    t = e.check_multi_existence()
                    if len(t) > 0:
                        e.do()
                        break
            elif node == NODE.fin:
                self.wait_for_connect()
                self.wait_for_load()
                self.battle()
                self.select_ego_gift()
                self.select_sinner()
                self.select_id()
                self.wait_for_connect()
                self.wait(2)
                conf.click()
                self.floor += 1

        pass

    def click_node(self, rect, forbid):
        if w_mir_road1.click(limit=rect, forbid=forbid):
            return NODE.battle, w_mir_road1.last_click
        if w_mir_road4.click(limit=rect, forbid=forbid):
            return NODE.battle, w_mir_road4.last_click
        elif w_mir_road3.click(limit=rect, forbid=forbid):
            return NODE.fin, w_mir_road3.last_click
        elif w_mir_road2.click(limit=rect, forbid=forbid):
            return NODE.event, w_mir_road2.last_click
        print('cannot find any node')
        return 0, 0

    def select_node(self):
        self.wait_for_panel(p_mir_road)
        if p_mir_road.is_current():
            forbid = []
            w_mir_mark.click()
            if self.floor % 2 == 0:
                rect = Rect(0, 0, w_mir_mark.last_click[0] - 0.09 * self.w, self.h)
            else:
                rect = Rect(w_mir_mark.last_click[0] + 0.09 * self.w, 0, self.w, self.h)

            self.wait()
            ev, last = self.click_node(rect, forbid)
            while type(last) != tuple:
                mouse.scroll(int(random.randint(-20, 20)))
                ev, last = self.click_node(rect, forbid)
            print(ev, last)
            x, y = last
            count = 0
            while not w_mir_road_enter.click():
                forbid.append(Rect(x - 5, y + 5, 10, 10))
                ev, last = self.click_node(rect, forbid)
                x, y = last
                self.wait()
                count += 1
                if count > 10:
                    raise Exception('我找不到')

            self.wait()

            if ev == NODE.battle or ev == NODE.fin:
                for v in range(12):
                    w_id_char_prefer[v].click()
                w_mir_combat.click()
            elif ev == NODE.event:
                pass

            return ev
        pass

    def battle(self):
        self.wait_for_panel(p_mir_battle)
        w_mir_battle1.click()
        self.wait()
        w_mir_battle2.click()
        break_count = 0
        while True:
            self.wait()
            print('check upgrade')
            # if w_mir_upgrade_title.is_exist():
            if p_mir_upgrade.is_current():
                print('find upgrade')
                break_count += 1
                if break_count > 2:
                    return self.upgrade_id()
            print('check ego')
            if p_mir_ego_chs.is_current():
                print('find ego')
                break_count += 1
                if break_count > 2:
                    return self.select_ego_gift()
            w_mir_battle1.click()
            self.wait()
            w_mir_battle2.click()
            pass

    def upgrade_id(self):
        for i in range(12):
            if w_id_char_prefer[i].click():
                conf.click()
                w_mir_upgrade_to_ego.click()
                w_mir_upgrade_ego_conf.click()

                self.wait_for_connect()
                conf.click()
                self.wait()
                self.get_img()
                if p_mir_road.is_current():
                    break

    def select_id(self):
        print('select id')
        self.wait()
        self.get_img()
        self.wait_for_panel(p_mir_id_chs1)
        for i in range(1, 13):
            if w_id_char_face[i - 1].click():
                w_id_char_prefer[i - 1].click()
                conf.click(2, auto_fetch=False)
        conf2.click()

    def select_sinner(self):
        print('select_sinner')
        prefer = [12, 5, 6, 8, 2]
        self.wait_for_panel(p_mir_char_chs)
        for v in prefer:
            w_chars_id[v - 1].click()
        cur = 1
        self.get_img()
        w_mir_char_conf.check_existence()
        while w_mir_char_conf.state != 2:
            if cur not in prefer:
                w_chars_id[cur - 1].click()
            cur += 1
            if cur == 12:
                break
        w_mir_char_conf.click()

    def select_ego_gift(self):
        print('select_ego_gift')
        self.get_img()
        self.wait_for_panel(p_mir_ego_chs)
        w_ego_frame.click()
        w_ego_conf.click()
        self.wait()
        conf.click()
        pass

    def do_frame(self):
        ui_init.click()
        self.to(p_mirror1_conf)
        w_mirror1_simu.click()
        w_mirror1_conf.click()
        self.mirror_dungeon()

        return True

    def frame_func(self):
        for e in events:
            e.father.father = self
        self.get_img()
        self.update_ptr()
        self.do_frame()


for root, dirs, files in os.walk("comp_history"):
    for file in files:
        path = os.path.join(root, file)
        os.remove(path)

game = LimbusCorp('LimbusCompany', 0.6)

ui_init = Widget_Simple('ui_init')

conf = Widget_Simple('conf')
conf2 = Widget_Simple('conf2')
to = Widget_Simple('to')
loading = Widget_Simple('ui_loading')
connecting = Widget_Simple('ui_connect')
retry = Widget_Simple('ui_retry')

p_main = Panel('非第三个主界面')
w3 = Widget_Auto('ui_w3')

p_main3 = Panel('第三个主界面')
w3.is_the_way_to(p_main3)
w3p = Widget_Auto('ui_w3p')
w_mirror_enter = Widget_Auto('ui_mirror_enter')

p_mirror_chs = Panel('镜牢选择')
w_mirror_enter.is_the_way_to(p_mirror_chs)
w_dung1 = Widget_Auto('ui_dung1')

p_mirror1_conf = Panel('镜牢1确认')
w_dung1.is_the_way_to(p_mirror1_conf)
w_mirror1_conf = Widget_Auto('ui_conf')
w_mirror1_simu = Widget_Simple('ui_simu')

p_mir_ego_chs = Panel('镜牢ego选择')
w_mirror1_conf.is_the_way_to(p_mir_ego_chs)
w_ego_frame = Widget_Auto('ego_frame')
w_ego_conf = Widget_Auto('ego_conf')

p_mir_char_chs = Panel('镜牢罪人选择')
w_chars_id_c = Widget_Auto(['icon_sinner%d' % i for i in range(1, 13)])
w_chars_id = [Widget_Simple('icon_sinner%d' % i) for i in range(1, 13)]
w_mir_char_conf = Widget_Simple('sinner_conf')

p_mir_id_chs1 = Panel('镜牢罪人人格选择')
w_id_sel1 = Widget_Auto('id_sel').set_confidence(0.65)
w_id_char_face = [Widget_Simple('sinner%d' % i) for i in range(1, 13)]
w_id_char_prefer = [Widget_Simple('sinner_pre%d' % i).set_confidence(0.85) for i in range(1, 13)]

p_mir_road = Panel('镜牢路线')
w_mir_mark = Widget_Auto('icon_current').set_confidence(0.65)
w_mir_road1 = Widget_Simple('road_combat').set_confidence(0.75)
w_mir_road4 = Widget_Simple('road_abnorm').set_confidence(0.75)
w_mir_road2 = Widget_Simple('road_event').set_confidence(0.75)
w_mir_road3 = Widget_Simple('road_fin').set_confidence(0.75)
w_mir_road_enter = Widget_Simple('road_enter')
w_mir_combat = Widget_Simple('ui_combat')

p_mir_battle = Panel('镜牢打架')
w_mir_battle = Widget_Auto('battle_c')
w_mir_battle1 = Widget_Simple('battle_step1')
w_mir_battle2 = Widget_Simple('battle_step2')

p_mir_upgrade = Panel('镜牢升级')
w_mir_upgrade_title = Widget_Auto('battle_upgrade')
w_mir_upgrade_to_ego = Widget_Simple('battle_upgrade_to_ego')
w_mir_upgrade_ego_conf = Widget_Simple('ego_conf2')

p_mir_event = Panel('镜牢事件')
w_mir_event_c = Widget_Auto('event_c')
w_mir_event_skip = Widget_Simple('ui_skip')
w_mir_event_btn = Widget_Simple('event_btn')
w_mir_event_con = Widget_Simple('event_con')

# game.floor = 1
# game.get_img()
# game.select_node()
game.frame_func()
