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
from screenshot import window_capture
from recognition import find_target
from baseImage import Image, Rect


class Game:
    def __init__(self, title, fps):
        self.title = title
        self.fps = fps
        self._wait = 1.0 / fps
        self.timer = 1
        self.cur = None
        self.vertexes = dict()

    def frame_func(self):
        stt = time.time()
        while True:
            try:
                self.do_frame()
            except Exception as err:
                print(err)
                self.cur = None
            self.timer += 1
            time.sleep(max(0, time.time() - stt + self._wait))
            stt = time.time()

        pass

    def do_frame(self):
        print('\rcurrent timer is:', self.timer, 'current time is:', time.time(), 'current panel:', self.cur)

        self.img = Image(window_capture(self.title))
        if self.cur is None or not self.vertexes[self.cur].is_current():
            print('find current panel:')
            for k, v in self.vertexes.items():
                print('\tin ', k, end=' ')
                if v.is_current():
                    self.cur = k
                    print('FIND!', k)
                    break

        pass

    def register_vertex(self, tag, vertex):
        # print('register_vertex',tag, vertex)
        if type(tag) == str:
            self.vertexes[tag] = vertex
        else:
            for t, v in zip(tag, vertex):
                self.vertexes[t] = v


class Panel:
    def __init__(self, father):
        self.father = father
        self.edges = list()
        self.widgets = list()
        pass

    def register_edge(self, other_vertex, correspond_widget):
        pass

    def register_widget(self, tag):
        pass

    def is_current(self):
        flag = True
        for v in self.widgets:
            x, y, c = v.check_existence()
            # print('check position:', v.c_path, x, y)
            flag = flag and (x is not None) and (y is not None)
            if not flag:
                print('not this')
                return False
            else:
                print("%.2f%%" % (c * 100), end=',')
        if flag:
            return True
        pass

    def do_task(self):
        pass

    def to(self, from_panel, to_panel):

        pass


class Widget:
    def __init__(self, c_path, father: Panel):
        self.c_path = c_path
        self.father = father
        self.img = Image(c_path)
        father.widgets.append(self)

    def check_existence(self):
        img = self.father.father.img
        t = find_target(img, self.img)
        if len(t) > 0:
            return t[0][0], t[0][1], t[0][2]
        else:
            return None, None, None

    def click(self):
        pass
        if self.father.is_current():
            pass
        else:
            pass


if __name__ == '__main__':
    pass