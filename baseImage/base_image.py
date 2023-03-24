# -*- coding: utf-8 -*-
import cv2
import numpy as np

from .constant import Place, SHOW_INDEX, Setting, CUDA_CVT_CHANNELS
from .coordinate import Rect, Size
from .utils.api import read_image, bytes_2_img, cvType_to_npType, npType_to_cvType


try:
    cv2.cuda.GpuMat
except AttributeError:
    cv2.cuda.GpuMat = cv2.cuda_GpuMat


class BaseImage(object):
    def __init__(self, data, read_mode=cv2.IMREAD_COLOR, dtype=np.uint8, place=None, clone=True,
                 bufferPool=None, stream=None):
        """
        基础构造函数

        Args:
            data(str|bytes|np.ndarray|cv2.cuda.GpuMat|cv2.UMat): 图片数据
                str: 接收一个文件路径,读取该路径的图片数据,转换为ndarray
                bytes: 接收bytes,转换为ndarray
                cv2.UMat|cv2.cuda.GpuMat: 接收opencv的图片格式

            read_mode(int): 写入图片的cv flags
            dtype: 数据格式
            place: 数据存放的方式(np.ndarray|cv2.cuda.GpuMat)
            clone(bool): if True图片数据会被copy一份新的, if False则不会拷贝
            bufferPool: cuda缓冲池
            stream: cuda流

        Returns:
             None
        """
        self._data = data
        self._read_mode = read_mode
        self._dtype = dtype
        self._place = place or Setting.Default_Place
        self._stream = stream or Setting.Default_Stream
        self._bufferPool = bufferPool or Setting.Default_Pool

        if data is not None:
            self.write(data, clone=clone)

    def write(self, data, read_mode=None, dtype=None, place=None, clone=True):
        """
        写入图片数据

        Args:
            data(str|bytes|np.ndarray|cv2.cuda.GpuMat): 图片数据
            read_mode(int): 写入图片的cv flags
            dtype: 数据格式(np.float|np.uint8|...)
            place: 数据存放的方式(np.ndarray|cv2.cuda.GpuMat)
            clone(bool): if True图片数据会被copy一份新的, if False则不会拷贝

        Returns:
             None

        """
        read_mode = read_mode or self._read_mode
        dtype = dtype or self.dtype
        place = place or self._place

        # logger.debug(f'输入type={type(data)}, id={id(data)}, place={place}')

        if isinstance(data, BaseImage):
            data = data.data

        """
        1、当data是字符串或者字节流的时候,转换成np.ndarray
        2、当data是np.ndarray|cv2.cuda.GpuMat|cv2.UMat时
            if clone: 拷贝一份新的
            if not clone: 不拷贝
        3、根据place转换data的类型
        4、根据dtype转换data的数据类型
        """
        if isinstance(data, (str, bytes)):  # data: np.ndarray
            if isinstance(data, str):
                data = read_image(data, flags=read_mode)
            elif isinstance(data, bytes):
                data = bytes_2_img(data)
        else:
            if clone:
                if isinstance(data, np.ndarray):
                    data = data.copy()
                elif isinstance(data, cv2.cuda.GpuMat):
                    data = data.copyTo(dst=self._create_gpu_mat(data=data, dtype=data.type()), stream=self._stream)
                elif isinstance(data, cv2.UMat):
                    data = cv2.UMat(data)

        self._data = data
        # 先转换类型,再转换数据格式
        self.place_convert(place=place)
        self.dtype_convert(dtype=dtype)
        # logger.debug(f'输出type={type(self._data)}, id={id(self._data)}, place={place}')

    def _create_gpu_mat(self, data, dtype):
        """
        从缓冲区创建图片对象

        Args:
            data(np.ndarray/Umat/GpuMat/Size/(rows, clos)): 创建相同大小的矩阵
            dtype: 图片数据类型(opencv)

        Returns:
            图片对象
        """
        if isinstance(data, (np.ndarray, cv2.UMat, cv2.cuda.GpuMat)):
            shape = self.get_shape(data)
            rows, cols = shape[:-1]
        elif isinstance(data, Size):
            rows = data.height
            cols = data.width
        elif isinstance(data, (tuple, list)):
            rows, cols = data
        else:
            raise ValueError('Unknown param, data={}, dtype={}'.format(data, dtype))

        if self._bufferPool:
            gpu_mat = self._bufferPool.getBuffer(rows=rows, cols=cols, type=dtype)
        else:
            gpu_mat = cv2.cuda.GpuMat(rows=rows, cols=cols, type=dtype)
        return gpu_mat

    def dtype_convert(self, dtype):
        """
        图片数据类型转换

        Args:
            dtype: 目标数据类型

        Returns:
            data(np.ndarray, cv2.cuda.GpuMat): 图片数据
        """
        data = self._data

        if isinstance(data, np.ndarray):
            if data.dtype != dtype:
                data = data.astype(dtype=dtype)
        elif isinstance(data, cv2.UMat):
            _data: np.ndarray = data.get()
            if _data.dtype != dtype:
                data = _data.astype(dtype=dtype)
                data = cv2.UMat(data)
        elif isinstance(data, cv2.cuda.GpuMat):
            if cvType_to_npType(data.type(), channels=data.channels()) != dtype:
                cv_type = npType_to_cvType(dtype, data.channels())
                data = data.convertTo(cv_type, dst=self._create_gpu_mat(data=data, dtype=cv_type), stream=self._stream)
        else:
            raise ValueError('Unknown data, type:{}, data={} '.format(type(data), data))

        self._data = data
        self._dtype = dtype

    def place_convert(self, place):
        """
        图片数据格式转换

        Args:
            place: 目标数据格式

        Returns:
            data: 图片数据
        """
        data = self._data

        if place == Place.Ndarray:
            if type(data) == np.ndarray:
                pass
            elif isinstance(data, cv2.cuda.GpuMat):
                data = data.download()
            elif isinstance(data, cv2.UMat):
                data = data.get()

        elif place == Place.GpuMat:
            if isinstance(data, (np.ndarray, cv2.UMat)):
                gpu_mat = self._create_gpu_mat(data=data, dtype=self.get_cv_dtype(data))
                gpu_mat.upload(data, self.stream)
                data = gpu_mat
            elif isinstance(data, cv2.cuda.GpuMat):
                pass
        elif place == Place.UMat:
            if isinstance(data, np.ndarray):
                data = cv2.UMat(data)
            elif isinstance(data, cv2.cuda.GpuMat):
                data = cv2.UMat(data.download())
            elif isinstance(data, cv2.UMat):
                pass
        else:
            raise ValueError('Unknown data, type:{}, data={} '.format(type(data), data))

        self._data = data
        self._place = place

    @property
    def shape(self):
        """
        获取图片的长、宽、通道数

        Returns:
            shape: (长,宽,通道数)/(rows, cols, channels)
        """
        return self.get_shape(self.data)

    @property
    def size(self):
        """
        获取图片的长、宽

        Returns:
            shape: (长,宽)/(rows, cols)
        """
        return self.shape[:-1]

    @property
    def channels(self):
        """
        获取图片的通道数

        Returns:
            channels: 通道数
        """
        if self.place == Place.Ndarray:
            return self.shape[2]
        elif self.place == Place.GpuMat:
            return self.data.channels()
        elif self.place == Place.UMat:
            return self.shape[2]

    @property
    def dtype(self):
        """
        获取图片numpy格式的数据类型

        Returns:
            dtype: 数据类型(numpy)
        """
        return self._dtype

    @property
    def cv_dtype(self):
        """
        获取图片opencv格式的数据类型

        Returns:
            dtype: 数据类型(opencv)
        """
        return self.get_cv_dtype(self.data)

    @property
    def cv_dtype_no_channels(self):
        """
        获取图片opencv格式的数据类型(不带通道数)

        Returns:
            dtype: 不带通道数的数据类型(opencv)
        """
        dtype = self.get_cv_dtype(self.data)
        channels = self.channels
        return dtype - ((channels - 1) * 8)

    @property
    def place(self):
        return self._place

    @property
    def data(self):
        return self._data

    @property
    def stream(self):
        return self._stream

    @staticmethod
    def get_cv_dtype(data):
        """
        根据data类型,获取cv格式的图片数据类型

        Args:
            data: 图片数据

        Returns:
            dtype: opencv的图片数据类型
        """
        if isinstance(data, np.ndarray):
            channels = BaseImage.get_shape(data)[2]
            dtype = data.dtype
            dtype = npType_to_cvType(dtype, channels)
        elif isinstance(data, cv2.cuda.GpuMat):
            dtype = data.type()
        elif isinstance(data, cv2.UMat):
            mat = data.get()
            channels = BaseImage.get_shape(mat)[2]
            dtype = mat.dtype
            dtype = npType_to_cvType(dtype, channels)
        else:
            raise ValueError('Unknown data, type:{}, data={} '.format(type(data), data))

        return dtype

    @staticmethod
    def get_np_dtype(data):
        """
        根据data类型,获取numpy格式的图片数据类型

        Args:
            data: 图片数据

        Returns:
            dtype: numpy的图片数据类型
        """
        if isinstance(data, np.ndarray):
            dtype = data.dtype
        elif isinstance(data, cv2.cuda.GpuMat):
            dtype = data.type()
            dtype = cvType_to_npType(dtype, data.channels())
        elif isinstance(data, cv2.UMat):
            mat = data.get()
            dtype = mat.dtype
        else:
            raise ValueError('Unknown data, type:{}, data={} '.format(type(data), data))

        return dtype

    @staticmethod
    def get_shape(data):
        """
        根据data类型,获取长、宽、通道数

        Args:
            data: 图片数据

        Returns:
            shape: (长,宽,通道数)
        """
        if isinstance(data, np.ndarray):
            shape = data.shape
        elif isinstance(data, cv2.cuda.GpuMat):
            shape = data.size()[::-1] + (data.channels(),)
        elif isinstance(data, cv2.UMat):
            shape = data.get().shape
        else:
            raise ValueError('Unknown data, type:{}, data={} '.format(type(data), data))

        if len(shape) == 2:
            shape = shape + (1,)

        return shape


class Image(BaseImage):
    def clone(self):
        """
        拷贝一个新图片对象

        Returns:
            Image: 新图片对象
        """
        return Image(data=self._data, read_mode=self._read_mode, dtype=self.dtype, place=self.place,
                     bufferPool=self._bufferPool, stream=self.stream)

    def _clone_with_params(self, data, **kwargs):
        """
        用data拷贝一个新图片对象(保留原Image对象的dtype|read_mode|place)

        Args:
            data: 图片数据

        Returns:
            Image: 新图片对象
        """
        clone = kwargs.pop('clone', True)
        return Image(data=data, read_mode=self._read_mode, dtype=self.dtype, place=self.place, clone=clone,
                     bufferPool=self._bufferPool, stream=self.stream)

    def rotate(self, code, stream=None):
        """
        旋转图片

        Args:
            code: 可选90度180度270度(顺时针)
            stream: cuda流

        Returns:
            Image: 旋转后的图片
        """
        assert code in (cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_90_CLOCKWISE)

        if self.place in (Place.Ndarray, Place.UMat):
            data = cv2.rotate(self.data, code)
        elif self.place == Place.GpuMat:
            stream = stream or self._stream
            if code == cv2.ROTATE_180:
                size = self.size[::-1]
                angle = 180
                offset_x, offset_y = size
            elif code == cv2.ROTATE_90_CLOCKWISE:
                size = self.size
                angle = 90
                offset_y = size[1]
                offset_x = 0
            else:
                size = self.size
                angle = 270
                offset_y = 0
                offset_x = size[0]
            dst = self._create_gpu_mat(size[::-1], dtype=self.cv_dtype)
            data = cv2.cuda.rotate(self.data, size, angle, xShift=offset_x, yShift=offset_y, stream=stream, dst=dst)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))
        return self._clone_with_params(data, clone=False)

    def resize(self, *args, **kwargs):
        """
        图片缩放

        Args:
            w: 宽
            h: 高
            size: (w,h)
            code: 差值方法
            stream: cuda流

        Returns:
            缩放后的图片
        """
        code = kwargs.get('code', cv2.INTER_LINEAR)
        stream = kwargs.get('stream', None)

        if kwargs.get('size'):
            size = kwargs.get('size')
            if isinstance(size, Size):  # args: (size=Size(100, 100), code=2)
                w, h = size.width, size.height
            elif isinstance(size, (tuple, list)):  # args: (size=(100, 100), code=2)
                w, h = size
            else:
                raise ValueError('Unknown params args={}, kwargs={}'.format(args, kwargs))
        elif kwargs.get('w') and kwargs.get('h'):  # args: (w=100, h=100, code=2)
            w, h = kwargs.get('w'), kwargs.get('h')
        else:
            args_len = len(args)
            if args_len in (1, 2):
                if args_len == 1:  # args:(Size(100, 100)) or ((100, 100))
                    arg = args[0]
                else:
                    if isinstance(args[0], (Size, tuple, list)):  # args:(Size(100, 100),2) or ((100, 100), 2)
                        arg, code = args
                    else:  # args:(100, 100) or Size(100, 100)
                        arg = args

                if isinstance(arg, Size):
                    w, h = arg.width, arg.height
                elif isinstance(arg, (tuple, list)):
                    if len(arg) == 2:
                        w, h = arg
                    else:
                        raise ValueError('Unknown params args={}, kwargs={}'.format(args, kwargs))
                else:
                    raise ValueError('Unknown params args={}, kwargs={}'.format(args, kwargs))
            elif args_len == 3:
                w, h, code = args
            else:
                raise ValueError('Unknown params args={}, kwargs={}'.format(args, kwargs))

        assert type(w) == int, '参数必须是int类型, args={}, kwargs={}'.format(args, kwargs)
        assert type(h) == int, '参数必须是int类型 args={}, kwargs={}'.format(args, kwargs)
        assert type(code) == int, '参数必须是int类型 args={}, kwargs={}'.format(args, kwargs)

        return self._resize(w=w, h=h, code=code, stream=stream)

    def _resize(self, w, h, code=cv2.INTER_LINEAR, stream=None):
        size = (w, h)
        if self.place in (Place.Ndarray, Place.UMat):
            data = cv2.resize(self.data, size, interpolation=code)
        elif self.place == Place.GpuMat:
            stream = stream or self._stream
            dst = self._create_gpu_mat(Size(w, h), dtype=self.cv_dtype)
            data = cv2.cuda.resize(self.data, size, interpolation=code, stream=stream, dst=dst)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))
        return self._clone_with_params(data, clone=False)

    def cvtColor(self, code, stream=None):
        """
        转换图片颜色空间

        Args:
            code(int): 颜色转换代码 https://docs.opencv.org/4.x/d8/d01/group__imgproc__color__conversions.html#ga4e0972be5de079fed4e3a10e24ef5ef0
            stream: cuda流

        Returns:
            Image: 转换后的新图片
        """
        if self.place in (Place.Ndarray, Place.UMat):
            data = cv2.cvtColor(self.data, code)
        elif self.place == Place.GpuMat:
            stream = stream or self._stream
            dst = self._create_gpu_mat(data=self.data, dtype=npType_to_cvType(self.dtype, CUDA_CVT_CHANNELS[code]))
            data = cv2.cuda.cvtColor(self.data, code, stream=stream, dst=dst)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))

        return self._clone_with_params(data, clone=False)

    def crop(self, rect):
        """
        区域范围截图

        Args:
            rect: 需要截图的范围

        Returns:
             Image: 截取的区域
        """
        height, width = self.size
        if not Rect(0, 0, width, height).contains(rect):
            raise OverflowError('Rect不能超出屏幕 rect={}, tl={}, br={}'.format(rect, rect.tl, rect.br))
        if self.place == Place.Ndarray:
            x_min, y_min = int(rect.tl.x), int(rect.tl.y)
            x_max, y_max = int(rect.br.x), int(rect.br.y)
            data = self.data[y_min:y_max, x_min:x_max].copy()
        elif self.place == Place.GpuMat:
            """
            cv2.cuda.GpuMat(gpuMat, roi) 这个构造函数在传入roi时,不会对gpuMat进行拷贝,具体的原因参考c++代码实现
            这会造成,裁剪后,gpuMat指向的指针不会被释放.

            例：
                原图: gpuMat占用3MB, crop_mat占用1MB.
                不拷贝: 裁剪完成后,占用显存3MB.
                       释放gpuMat后,仍然占用3MB
                拷贝: 裁剪完成后,占用显存4MB(gpuMat+crop_mat).
                     释放gpuMat后,占用1MB(4MB-gpuMat)
            """
            crop_mat = cv2.cuda.GpuMat(self.data, rect.totuple())
            data = self._create_gpu_mat(rect.size, dtype=self.cv_dtype)
            crop_mat.copyTo(data)
        elif self.place == Place.UMat:
            data = cv2.UMat(self.data, rect.totuple())
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))

        return self._clone_with_params(data, clone=False)

    def threshold(self, thresh=0, maxval=255, code=cv2.THRESH_OTSU, stream=None):
        """
        图片二值化

        Args:
            thresh: 阈值
            maxval: 最大值
            code: type of the threshold operation
            stream: cuda流

        Returns:
             Image: 二值化后的图片
        """
        if self.place in (Place.Ndarray, Place.UMat):
            _, data = cv2.threshold(self.data, thresh, maxval, code)
        elif self.place == Place.GpuMat:
            if code > 4:
                # cuda threshold不支持这两种方法,需要转换
                _, data = cv2.threshold(self.data.download(), thresh, maxval, code)
            else:
                stream = stream or self._stream
                dst = self._create_gpu_mat(data=self.data, dtype=self.cv_dtype)
                _, data = cv2.cuda.threshold(self.data, thresh, maxval, code, stream=stream, dst=dst)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))
        return self._clone_with_params(data, clone=False)

    def rectangle(self, rect, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_8):
        """
        在图像上画出矩形, 注!绘制会在原图上进行,不会产生新的图片对象

        Args:
            rect(Rect): 需要截图的范围
            color(tuple): 表示矩形边框的颜色
            thickness(int): 形边框的厚度
            lineType(int): 线的类型

        Returns:
             None
        """
        pt1 = rect.tl
        pt2 = rect.br

        if self.place in (Place.Ndarray, Place.UMat):
            cv2.rectangle(self.data, (pt1.x, pt1.y), (pt2.x, pt2.y), color=color, thickness=thickness, lineType=lineType)
        elif self.place == Place.GpuMat:
            data = cv2.rectangle(self.data.download(), (pt1.x, pt1.y), (pt2.x, pt2.y), color=color, thickness=thickness, lineType=lineType)
            self.data.upload(data, self.stream)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))

    def copyMakeBorder(self, top, bottom, left, right, borderType, stream=None):
        """
        扩充边缘

        Args:
            top(int): 上扩充大小
            bottom(int): 下扩充大小
            left(int): 左扩充大小
            right(int): 右扩充大小
            borderType(int): 边缘扩充类型
            stream: cuda流

        Returns:
            扩充后的图像
        """
        if self.place in (Place.Ndarray, Place.UMat):
            data = cv2.copyMakeBorder(self.data, top, bottom, left, right, borderType)
        elif self.place == Place.GpuMat:
            stream = stream or self._stream
            size = Size(self.size[0] + left + right, self.size[1] + top + bottom)
            dst = self._create_gpu_mat(size, dtype=self.cv_dtype)
            data = cv2.cuda.copyMakeBorder(self.data, top, bottom, left, right, borderType, stream=stream, dst=dst)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))
        return self._clone_with_params(data, clone=False)

    def gaussianBlur(self, size=(11, 11), sigma=1.5, borderType=cv2.BORDER_DEFAULT, stream=None):
        """
        使用高斯滤镜模糊图像

        Args:
            size(tuple): 高斯核大小
            sigma(int|float): 高斯核标准差
            borderType(int): pixel extrapolation method
            stream: cuda流
        Returns:
             Image: 高斯滤镜模糊图像
        """
        if not (size[0] % 2 == 1) or not (size[1] % 2 == 1):
            raise ValueError('Window size must be odd.')

        if self.place in (Place.Ndarray, Place.UMat):
            data = cv2.GaussianBlur(self.data, ksize=size, sigmaX=sigma, sigmaY=sigma, borderType=borderType)
        elif self.place == Place.GpuMat:
            dtype = self.data.type()
            # TODO: 感觉可以优化
            stream = stream or self._stream
            gaussian = cv2.cuda.createGaussianFilter(dtype, dtype, ksize=size, sigma1=sigma, sigma2=sigma,
                                                     rowBorderMode=borderType, columnBorderMode=borderType)
            dst = self._create_gpu_mat(self.data, dtype=self.cv_dtype)
            data = gaussian.apply(self.data, stream=stream, dst=dst)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))
        return self._clone_with_params(data, clone=False)

    def warpPerspective(self, matrix, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0, stream=None):
        """
        透视变换

        Args:
            matrix: 3x3变换矩阵
            size: 输出图像的大小
            flags: 插值方法
            borderMode: 像素外推法
            borderValue: 边界值
            stream: cuda流

        Returns:
            透视变换后的图片
        """
        if isinstance(size, Size):
            w = size.width
            h = size.height
        elif isinstance(size, (tuple, list)):
            w = size[0]
            h = size[1]
        else:
            raise ValueError('size必须为Size/tuple/list')

        if self.place in (Place.Ndarray, Place.UMat):
            data = cv2.warpPerspective(self.data, matrix, (w, h), flags=flags, borderMode=borderMode, borderValue=borderValue)
        elif self.place == Place.GpuMat:
            stream = stream or self._stream
            dst = self._create_gpu_mat(Size(w, h), dtype=self.cv_dtype)
            data = cv2.cuda.warpPerspective(self.data, matrix, (w, h), flags=flags, dst=dst,
                                            borderMode=borderMode, borderValue=borderValue, stream=stream)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))
        return self._clone_with_params(data, clone=False)

    def bitwise_not(self, mask=None, stream=None):
        """
        反转图片颜色

        Args:
            mask: 掩码
            stream: cuda流

        Returns:
             Image: 反转后的图片
        """
        if self.place in (Place.Ndarray, Place.UMat):
            data = cv2.bitwise_not(self.data, mask=mask)
        elif self.place == Place.GpuMat:
            stream = stream or self._stream
            dst = self._create_gpu_mat(self.data, dtype=self.cv_dtype)
            data = cv2.cuda.bitwise_not(self.data, mask=mask, stream=stream, dst=dst)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))

        return self._clone_with_params(data, clone=False)

    def imshow(self, title=None, flags=cv2.WINDOW_KEEPRATIO):
        """
        以GUI显示图片

        Args:
            title(str): cv窗口的名称, 不填写会自动分配
            flags(int): 窗口类型

        Returns:
            None
        """
        title = str(title or SHOW_INDEX())
        cv2.namedWindow(title, flags)

        data = self.data
        if self.dtype != np.uint8:
            data = Image(data=data, dtype=np.uint8).data

        if isinstance(data, (np.ndarray, cv2.UMat)):
            cv2.imshow(title, data)
        elif isinstance(data, cv2.cuda.GpuMat):
            cv2.imshow(title, data.download())

    def imwrite(self, file_name):
        """
        将图片保存到指定路径

        Args:
            file_name: 文件路径

        Returns:
            None
        """
        data = self.data
        if isinstance(data, (np.ndarray, cv2.UMat)):
            cv2.imwrite(file_name, data)
        elif isinstance(data, cv2.cuda.GpuMat):
            cv2.imwrite(file_name, data.download())

    def split(self, stream=None):
        """
        拆分图像通道

        Args:
            stream: cuda流

        Returns:
            拆分后的图像数据,不会对数据包装处理
        """
        if self.place in (Place.Ndarray, Place.UMat):
            data = cv2.split(self.data)
        elif self.place == Place.GpuMat:
            stream = stream or self._stream
            dst = [self._create_gpu_mat(data=self.data, dtype=self.cv_dtype_no_channels) for i in range(self.channels)]
            data = cv2.cuda.split(self.data, stream=stream, dst=dst)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))
        return data

    def calcHist(self, histSize, ranges, mask=None, accumulate=False, stream=None):
        """
        计算图像颜色直方图

        Args:
            histSize: 直方图每一个维度划分的柱条的数目
            ranges: 取值区间
            mask: 掩模
            accumulate: 在多个图像时，是否累积计算像素值的个数
            stream: cuda流

        Returns:
            各通道的直方图数组
        """
        hists = []
        data = self.data

        if self.place == Place.GpuMat:
            data = self.data.download(stream=stream)

        for i in range(self.channels):
            hists.append(cv2.calcHist([data], [i], mask=mask, histSize=histSize, ranges=ranges, accumulate=accumulate))
            # stream = stream or self._stream
            # data = self.split(stream)
            # dst = [self._create_gpu_mat((1, 256), dtype=cv2.CV_32SC1) for i in range(self.channels)]
            # for i in range(self.channels):
            #     hists.append(cv2.cuda.calcHist(data[i], hist=dst[i], stream=stream))
            # [np.rot90(i.download(), 3) for i in hists]
        return hists

    def inRange(self, lowerb, upperb, stream=None):
        """
        检查数组元素是否位于两个标量之间

        Args:
            lowerb: 下边界
            upperb: 上边界
            stream: cuda流

        Returns:
            二值化后的数组
        """
        if self.place in (Place.Ndarray, Place.UMat):
            data = cv2.inRange(self.data, lowerb, upperb)
        elif self.place == Place.GpuMat:
            stream = stream or self._stream
            dst = self._create_gpu_mat(data=self.data, dtype=cv2.CV_8UC1)
            data = cv2.cuda.inRange(self.data, lowerb, upperb, dst=dst, stream=stream)
        else:
            raise TypeError("Unknown place:'{}', image_data={}, image_data_type".format(self.place, self.data, type(self.data)))

        return self._clone_with_params(data, clone=False)
