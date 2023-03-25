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


def _check(src,rsc):
    match = SIFT(threshold=0.86)
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


debug=True
_cur = 1


def find_target(im_source, im_search):
    match = SIFT(threshold=0.8)
    # im_source = Image('1.png')
    # im_search = Image('1.png').crop(Rect(681,239,48,48))

    if debug:
        global _cur
        im_source.imwrite("comp_history\\%d_im_source.bmp"%_cur)
        im_search.imwrite("comp_history\\%d_im_search.bmp"%_cur)
        _cur = _cur + 1

    # start = time.time()
    result = match.find_all_results(im_source, im_search)
    # for _ in result:
    #     print(_['rect'])

    # print(time.time() - start)
    res = []
    for r in result:
        # print(r['rect'].x, r['rect'].y, r['confidence'])
        rec=r['rect']
        res.append((int(rec.x+rec.width/2), int(rec.y+rec.height/2), r['confidence']))
    return res
    # img = im_source.clone()
    # for _ in result:
    #     print(_['rect'])
    #     img.rectangle(rect=_['rect'], color=(0, 0, 255), thickness=3)
    # img.imshow('ret')
    # img.imwrite('1.jpg')
    # pass


# def find_target2(im_source, im_search,threshold=0.8):
#     res = aircv.find_template(im_source, im_search, threshold)
#     return res["result"] if res else (-1, -1)



if __name__ == '__main__':
    # _demo()
    for root, dirs, files in os.walk("comp_history"):
        twin=["",""]
        for i,file in enumerate(files):
            path = os.path.join(root, file)
            twin[i%2]=path
            if i%2==1:
                print('checking',twin[1],twin[0])
                _check(twin[1],twin[0])
