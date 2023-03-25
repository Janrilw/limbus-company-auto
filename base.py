#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" ================================
base.py
套娃结构：game->panel->widget
其中game等于一个图，panel等于一个节点，widget是单向边。
info:

- time: 2023/3/23 9:31
- author: 云绝万里
- email: janrilw@163.com
"""
import time

import numpy as np

from screenshot import window_capture
from recognition import find_target
from baseImage import Image, Rect
from mouse import click, move

# from PIL import Image,ImageGrab

cur_game = None
cur_panel = None


class Game:
    img: Image

    def __init__(self, title, fps):
        global cur_game
        cur_game = self
        self.title = title
        self.fps = fps
        self._wait = 1.0 / fps
        self.timer = 1
        self.cur = None
        self.vertexes = dict()
        self.stt = time.time()
        self._srh_heap = []
        self.offset_x, self.offset_y = 0, 0

    def frame_func(self):
        self.get_img()
        self.update_ptr()
        while True:
            try:
                if self.do_frame():
                    break
            except Exception as err:
                print(err)
                self.cur = None
            self.wait()

        pass

    def get_current(self):
        return self.vertexes[self.cur]

    def _search(self, cur, panel):
        print('\tcur:%s ; search:%s' % (cur.tag, panel.tag))
        self._srh_heap.append(cur)
        for p, w in cur.edges.items():
            print('\t edge of', cur.tag, 'point to', p.tag)
            if p in self._srh_heap:
                continue
            if p == panel:
                print('\t found path, path len is', len(self._srh_heap))
                return True
            else:
                return self._search(p, panel)
        self._srh_heap.pop()
        return False

    def to(self, panel):
        cur: Panel
        cur = self.get_current()
        self._srh_heap = []
        print('[searching path]', end='')
        self._search(cur, panel)
        self._srh_heap.append(panel)
        for i, v in enumerate(self._srh_heap):
            self.get_img()
            if i >= 1:
                self._srh_heap[i - 1].to(v)
                self.wait()

    def wait(self, n=1):
        for _ in range(n):
            if n > 1:
                print('\r', end='')
            print('[waiting], end of frame %d' % self.timer, end='')
            self.timer += 1
            time.sleep(max(0, -(time.time() - self.stt) + self._wait))
            self.stt = time.time()
            print('\r[waited], begin of frame %d' % self.timer)
        # print('\r', end='')

    def get_img(self):
        self.img, self.offset_x, self.offset_y = window_capture(self.title)
        return self.img

    def mouse_move_out(self, wait=True):
        move(self.offset_x, self.offset_y)
        if wait:
            self.wait()

    def update_ptr(self):
        print('\rcurrent timer is:', self.timer, 'current time is:', time.time(), 'current panel:', self.cur)
        if self.cur is None or not self.vertexes[self.cur].is_current():
            print('find current panel:')
            for k, v in self.vertexes.items():
                print('\tin ', k, end=' ')
                if v.is_current():
                    self.cur = k
                    print('FIND!', k)
                    break

    def do_frame(self):
        self.get_img()
        self.update_ptr()

    def register_vertex(self, tag, vertex):
        # print('register_vertex',tag, vertex)
        if type(tag) == str:
            self.vertexes[tag] = vertex
        else:
            for t, v in zip(tag, vertex):
                self.vertexes[t] = v


class Panel:
    father: Game

    def __init__(self, tag, father=None):
        global cur_panel, cur_game
        cur_panel = self
        if father is None:
            father = cur_game
        assert father
        self.father = father
        self.tag = tag
        father.register_vertex(tag, self)
        self.edges = dict()
        self.widgets = dict()
        self.tmp = None
        pass

    def register_edge(self, correspond_widget, other_vertex):
        self.edges[other_vertex] = correspond_widget
        pass

    def s(self, widget):
        self.tmp = widget
        return self
        pass

    def is_the_way_to(self, other_vertex):
        assert self.tmp is not None
        self.register_edge(self.tmp, other_vertex)
        self.tmp = None

    def register_widget(self, tag, widget):
        self.widgets[tag] = widget
        pass

    def is_current(self):
        if self.father.cur is not None:
            return self.tag == self.father.cur
        flag = True
        for v in self.widgets.values():
            x, y, c = v.check_existence()
            # print('check position:', v.c_path, x, y)
            flag = flag and (x is not None) and (y is not None)
            if not flag:
                print('not this')
                return False
            else:
                # print("%.2f%%" % (c * 100), end=',')
                pass
        if flag:
            return True
        pass

    def to(self, to_panel):
        print('move from', self.tag, 'to', to_panel.tag)
        x, y, c = self.edges[to_panel].check_existence()
        self.edges[to_panel]._click(x, y)


class Widget:
    def __init__(self, tag, c_path, father: Panel = None):
        global cur_panel
        if father is None:
            father = cur_panel
        assert father

        self.tag = tag
        self.c_path = c_path
        self.father = father
        self.img = Image(c_path)
        # self.img = np.array(Image.open(c_path))
        father.register_widget(tag, self)

    def check_existence(self):
        img = self.father.father.img
        t = find_target(img, self.img)
        print('find widget:%s' % self.tag, end=' | ')
        if len(t) > 0:
            return t[0][0], t[0][1], t[0][2]
        else:
            return 0, None, 0

    def _click(self, x, y):
        click(self.father.father.offset_x + x, self.father.father.offset_y + y)

    def click(self, x=None, y=None, auto_fetch=True):
        if auto_fetch:
            self.father.father.get_img()
        if x is None:
            param = self.check_existence()
            x, y, c = param
        if x is None:
            print('cannot find button!')
            return False
        else:
            self._click(x, y)

    def is_the_way_to(self, panel):
        self.father.register_edge(self, panel)


if __name__ == '__main__':
    pass
