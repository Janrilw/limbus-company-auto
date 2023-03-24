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
import cv2
import time

from baseImage import Image, Rect
from image_registration.matching import SIFT


def _demo():
    match = SIFT()
    im_source = Image('1.png')
    im_search = Image('1.png').crop(Rect(681, 239, 48, 48))

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


match = SIFT(threshold=0.54)


def find_target(im_source, im_search):
    # im_source = Image('1.png')
    # im_search = Image('1.png').crop(Rect(681,239,48,48))

    # start = time.time()
    result = match.find_all_results(im_source, im_search)
    # for _ in result:
    #     print(_['rect'])

    # print(time.time() - start)
    res = []
    for r in result:
        # print(r['rect'].x, r['rect'].y, r['confidence'])
        res.append((r['rect'].x, r['rect'].y, r['confidence']))
    return res
    # img = im_source.clone()
    # for _ in result:
    #     print(_['rect'])
    #     img.rectangle(rect=_['rect'], color=(0, 0, 255), thickness=3)
    # img.imshow('ret')
    # cv2.waitkey(0)
    # pass


if __name__ == '__main__':
    _demo()
