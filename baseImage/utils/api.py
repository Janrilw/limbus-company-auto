# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np

from baseImage.exceptions import ReadImageError


def check_file(file_name):
    """check file in path"""
    return os.path.isfile('{}'.format(file_name))


def check_image_valid(image):
    """检查图像是否有效"""
    if image is not None and image.any():
        return True
    else:
        return False


def read_image(filename, flags=cv2.IMREAD_COLOR):
    """cv2.imread的加强版"""
    if check_file(filename) is False:
        raise ReadImageError("File not found in path:'{}''".format(filename))

    img = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), flags)

    if check_image_valid(img):
        return img
    else:
        raise ReadImageError('cv2 decode Error, path:{}, flags={}', filename, flags)


def bytes_2_img(byte):
    """bytes转换成cv2可读取格式"""
    img = cv2.imdecode(np.array(bytearray(byte)), 1)
    if img is None:
        raise ValueError('decode bytes to image error')

    return img


def npType_to_cvType(dtype, channels):
    if dtype == np.uint8:
        num = 0
    elif dtype == np.int8:
        num = 1
    elif dtype == np.uint16:
        num = 2
    elif dtype == np.int16:
        num = 3
    elif dtype == np.int32:
        num = 4
    elif dtype == np.float32:
        num = 5
    elif dtype == np.float64:
        num = 6

    num = num + (channels - 1) * 8
    return num


def cvType_to_npType(dtype: int, channels: int):
    num = dtype - (channels - 1) * 8

    data_type = None

    if num == 0:
        data_type = np.uint8
    elif num == 1:
        data_type = np.int8
    elif num == 2:
        data_type = np.uint16
    elif num == 3:
        data_type = np.int16
    elif num == 4:
        data_type = np.int32
    elif num == 5:
        data_type = np.float32
    elif num == 6:
        data_type = np.float64

    return data_type


class AutoIncrement(object):
    def __init__(self):
        self._val = 0

    def __call__(self):
        self._val += 1
        return self._val
