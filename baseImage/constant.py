# -*- coding: utf-8 -*-
import cv2
import numpy as np

from .utils.api import AutoIncrement

SHOW_INDEX = AutoIncrement()


class Place(object):
    Ndarray = np.ndarray
    GpuMat = None
    UMat = cv2.UMat


class Setting(object):
    CUDA_Flag = False
    Default_Stream = None
    Default_Pool = None
    Default_Place = Place.Ndarray


if cv2.cuda.getCudaEnabledDeviceCount() > 0:
    Setting.CUDA_Flag = True
    Place.GpuMat = cv2.cuda.GpuMat


operations = {
    'mat': {
        'multiply': cv2.multiply,
        'subtract': cv2.subtract,
        'add': cv2.add,
        'pow': cv2.pow,
        'divide': cv2.divide,
        'merge': cv2.merge,
    },
    'cuda': {
        'multiply': None,
        'subtract': None,
        'add': None,
        'pow': None,
        'divide': None,
        'merge': None,
    }
}

if Setting.CUDA_Flag:
    operations['cuda'] = {
        'multiply': cv2.cuda.multiply,
        'subtract': cv2.cuda.subtract,
        'add': cv2.cuda.add,
        'pow': cv2.cuda.pow,
        'divide': cv2.cuda.divide,
        'merge': cv2.cuda.merge,
    }


CUDA_CVT_CHANNELS = {
    cv2.COLOR_BGR2BGR555: 2,
    cv2.COLOR_BGR2BGR565: 2,
    cv2.COLOR_BGR2BGRA: 4,
    cv2.COLOR_BGR2GRAY: 1,
    cv2.COLOR_BGR2HLS: 3,
    cv2.COLOR_BGR2HLS_FULL: 3,
    cv2.COLOR_BGR2HSV: 3,
    cv2.COLOR_BGR2HSV_FULL: 3,
    cv2.COLOR_BGR2LAB: 3,
    cv2.COLOR_BGR2LUV: 3,
    cv2.COLOR_BGR2Lab: 3,
    cv2.COLOR_BGR2Luv: 3,
    cv2.COLOR_BGR2RGB: 3,
    cv2.COLOR_BGR2RGBA: 4,
    cv2.COLOR_BGR2XYZ: 3,
    cv2.COLOR_BGR2YCR_CB: 3,
    cv2.COLOR_BGR2YCrCb: 3,
    cv2.COLOR_BGR2YUV: 3,
    cv2.COLOR_BGRA2BGR: 3,
    cv2.COLOR_BGRA2BGR555: 2,
    cv2.COLOR_BGRA2BGR565: 2,
    cv2.COLOR_BGRA2GRAY: 1,
    cv2.COLOR_BGRA2RGB: 3,
    cv2.COLOR_BGRA2RGBA: 4,

    cv2.COLOR_RGB2BGR: 3,
    cv2.COLOR_RGB2BGR555: 2,
    cv2.COLOR_RGB2BGR565: 2,
    cv2.COLOR_RGB2BGRA: 4,
    cv2.COLOR_RGB2GRAY: 1,
    cv2.COLOR_RGB2HLS: 3,
    cv2.COLOR_RGB2HLS_FULL: 3,
    cv2.COLOR_RGB2HSV: 3,
    cv2.COLOR_RGB2HSV_FULL: 3,
    cv2.COLOR_RGB2LAB: 3,
    cv2.COLOR_RGB2LUV: 3,
    cv2.COLOR_RGB2Lab: 3,
    cv2.COLOR_RGB2Luv: 3,
    cv2.COLOR_RGB2RGBA: 4,
    cv2.COLOR_RGB2XYZ: 3,
    cv2.COLOR_RGB2YCR_CB: 3,
    cv2.COLOR_RGB2YCrCb: 3,
    cv2.COLOR_RGB2YUV: 3,
    cv2.COLOR_RGBA2BGR: 3,
    cv2.COLOR_RGBA2BGR555: 2,
    cv2.COLOR_RGBA2BGR565: 2,
    cv2.COLOR_RGBA2BGRA: 4,
    cv2.COLOR_RGBA2GRAY: 1,
    cv2.COLOR_RGBA2RGB: 3,

    cv2.COLOR_GRAY2BGR: 3,
    cv2.COLOR_GRAY2BGR555: 2,
    cv2.COLOR_GRAY2BGR565: 2,
    cv2.COLOR_GRAY2BGRA: 4,
    cv2.COLOR_GRAY2RGB: 3,
    cv2.COLOR_GRAY2RGBA: 4,

}