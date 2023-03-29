#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" ================================
sandbox.py
尝试用SIFT识别图片内容
info:

- time: 2022/10/27 10:50
- author: 云绝万里
- email: janrilw@163.com
"""
import os

import cv2
import time

from baseImage import Image, Rect
from image_registration.matching import SIFT


# import aircv


def _demo():
    match = SIFT()
    im_source = Image('sample.jpg')
    im_search = Image('img_lcb\\w2.jpg')

    start = time.time()
    result = match.find_all_results(im_source, im_search)
    print(time.time() - start)
    for r in result:
        print(r)
    img = im_source.clone()
    for _ in result:
        print(_['rect'])
        img.rectangle(rect=_['rect'], color=(0, 0, 255), thickness=3)
    img.imshow('ret')
    cv2.waitKey(0)


def _check(src, rsc, th=0.86):
    match = SIFT(threshold=th)
    im_source = Image(src)
    im_search = Image(rsc)

    start = time.time()
    result = match.find_all_results(im_source, im_search)
    print(time.time() - start)
    for r in result:
        print(r)
    img = im_source.clone()
    for _ in result:
        print(_['rect'])
        img.rectangle(rect=_['rect'], color=(0, 0, 255), thickness=3)
    img.imshow('ret')
    cv2.waitKey(0)


def _path_source(v):
    return "comp_history\\%02d_im_source.bmp" % v


def _path_search(v):
    return "comp_history\\%02d_im_search.bmp" % v


_cur = 0


def find_target(im_source, im_search, threshold=0.75, debug=True):
    match = SIFT(threshold=threshold)


    if debug:
        os.makedirs('comp_history', exist_ok=True)
        global _cur
        im_source.imwrite(_path_source(_cur))
        im_search.imwrite(_path_search(_cur))
        _cur2 = _cur - 100
        if os.path.exists(_path_source(_cur2)):
            os.remove(_path_source(_cur2))
        if os.path.exists(_path_search(_cur2)):
            os.remove(_path_search(_cur2))
        _cur = _cur + 1

    result = match.find_all_results(im_source, im_search)
    res = []
    for r in result:
        rec = r['rect']
        res.append((int(rec.x + rec.width / 2), int(rec.y + rec.height * 0.75), r['confidence']))
    return res


if __name__ == '__main__':
    # _demo()
    # 用于debug的代码，如果开启了debug模式会记录最近100次匹配的原图和特征图
    choose = '234'
    for root, dirs, files in os.walk("comp_history"):
        twin = ["", ""]
        for i, file in enumerate(files):
            path = os.path.join(root, file)
            twin[i % 2] = path
            if i % 2 == 1:
                if choose in path:
                    print('checking', twin[1], twin[0])
                    _check(twin[1], twin[0], 0.5)
