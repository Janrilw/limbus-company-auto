from baseImage import Image, Rect
from baseImage.constant import Place, operations, Setting

import cv2
import numpy as np
from typing import Union, Optional, Tuple


class SSIM(object):
    def __init__(self, win_size: int = 11, data_range: int = 255, sigma: Union[int, float] = 1.5,
                 use_sample_covariance=True, resize=(500, 500)):
        """
        使用ssim计算两张图片的相似度

        Args:
            win_size(int): 高斯核大小
            data_range(int): 图片的取值范围 (1.0 or 255)
            sigma(float): 高斯核标准差
            use_sample_covariance: 如果为真，则通过 N-1 而不是 N 归一化
            resize: 输入图片的缩放大小(h, w)
        """
        self.win_size = win_size
        self.data_range = data_range
        self.sigma = sigma
        self.dtype = np.float32
        self.K1 = 0.01
        self.K2 = 0.03
        self.C1 = (self.K1 * self.data_range) ** 2
        self.C2 = (self.K2 * self.data_range) ** 2
        self.resize = resize

        NP = win_size ** 2
        # filter has already normalized by NP
        if use_sample_covariance:
            cov_norm = NP / (NP - 1)  # sample covariance
        else:
            cov_norm = 1.0  # population covariance to match Wang et. al. 2004
        self.cov_norm = cov_norm
        self.gaussian_args = {'size': (win_size, win_size), 'sigma': sigma, 'borderType': cv2.BORDER_REFLECT}

    #     if Setting.CUDA_Flag:
    #         self._buffer_cuda_mat()
    #
    # def _buffer_cuda_mat(self):
    #     # https://github.com/opencv/opencv/issues/18026
    #     size = self.resize
    #
    #     cov_norm = np.empty(size, dtype=np.float32)
    #     cov_norm.fill(self.cov_norm)
    #     self._cuda_cov_norm = cv2.cuda.GpuMat(size, cv2.CV_32F)
    #     self._cuda_cov_norm.upload(cov_norm)
    #
    #     C1 = np.empty(size, dtype=np.float32)
    #     C1.fill(self.C1)
    #     self._cuda_C1 = cv2.cuda.GpuMat(size, cv2.CV_32F)
    #     self._cuda_C1.upload(C1)
    #
    #     C2 = np.empty(size, dtype=np.float32)
    #     C2.fill(self.C2)
    #     self._cuda_C2 = cv2.cuda.GpuMat(size, cv2.CV_32F)
    #     self._cuda_C2.upload(C2)

    @classmethod
    def _image_check(cls, im1: Image, im2: Image):
        if not isinstance(im1, Image) and not isinstance(im2, Image):
            raise ValueError('im1 im2必须为Image类型, im1_type:{}, im2_type:{}'.format(type(im1), type(im2)))

        if im1.channels != im2.channels:
            raise ValueError('图片通道数量必须一致, im1:{}, im2:{}'.format(im1.place, im2.place))

        if im1.size != im2.size:
            raise ValueError('图片大小一致, im1:{}, im2:{}'.format(im1.size, im2.size))

        if im1.place != im2.place:
            im2 = Image(im2, place=im1.place, dtype=np.float32)

        if im1.dtype != np.float32:
            im1 = Image(im1, place=im1.place, dtype=np.float32)

        if im2.dtype != np.float32:
            im2 = Image(im2, place=im2.place, dtype=np.float32)
        return im1, im2

    def ssim(self, im1: Image, im2: Image, full: bool = False) -> Tuple[float, Optional[Image]]:
        """
        计算两张图片的相似度

        Args:
            im1: 图片1
            im2: 图片2
            full: if True 还返回完整的结构相似性图像。

        Returns:
            mssim(float): 结构相似度
            S(Image): if full==True 完整的结构相似性图像。
        """
        im1, im2 = self._image_check(im1=im1, im2=im2)
        size = self.resize[::-1]
        im1 = im1.resize(*size)
        im2 = im2.resize(*size)

        return self._ssim(im1=im1, im2=im2, full=full)

    def _ssim(self, im1: Image, im2: Image, full: bool = False):
        new_image_args = {'place': im1.place, 'dtype': self.dtype, 'clone': False}
        nch = im1.channels

        if nch > 1:
            im1 = im1.split()
            im2 = im2.split()
            mssim = np.empty(nch, dtype=np.float64)
            if full:
                S = []
            # 分割通道,计算每个通道的相似度,最后取平均值
            for ch in range(nch):
                result = self._ssim(im1=Image(data=im1[ch], **new_image_args),
                                    im2=Image(data=im2[ch], **new_image_args), full=full)
                if full:
                    mssim[ch], _s = result
                    S.append(_s.data)
                else:
                    mssim[ch] = result

            mssim = mssim.mean()
            if full:
                if new_image_args['place'] == Place.GpuMat:
                    S = operations['cuda']['merge'](S)
                else:
                    S = operations['mat']['merge'](S, nch)
                S = Image(data=S, place=new_image_args['place'], dtype=np.uint8)
                return mssim, S
            else:
                return mssim

        # 单通道处理
        result = self._cv_ssim(im1=im1, im2=im2, full=full)
        if full:
            mssim, S = result
            S = Image(data=S, place=new_image_args['place'], dtype=np.uint8)
            return mssim, S
        else:
            mssim = result
            return mssim

    def _cv_ssim(self, im1: Image, im2: Image, full: bool = False) -> Tuple[float, Optional[np.ndarray]]:
        """
        full返回的会是uint8格式
        """
        h, w = im1.shape[:2]
        new_image_args = {'place': im1.place, 'dtype': self.dtype, 'clone': False}
        cuda_flag = im1.place == Place.GpuMat
        umat_flag = im1.place == Place.UMat

        ux = im1.gaussianBlur(**self.gaussian_args).data
        uy = im2.gaussianBlur(**self.gaussian_args).data

        if cuda_flag:
            multiply = operations['cuda']['multiply']
            subtract = operations['cuda']['subtract']
            add = operations['cuda']['add']
            divide = operations['cuda']['divide']
            pow = operations['cuda']['pow']
        else:
            multiply = operations['mat']['multiply']
            subtract = operations['mat']['subtract']
            add = operations['mat']['add']
            divide = operations['mat']['divide']
            pow = operations['mat']['pow']

        cov_norm = self.cov_norm
        C1 = self.C1
        C2 = self.C2

        uxx = Image(data=multiply(im1.data, im1.data), **new_image_args).gaussianBlur(**self.gaussian_args).data
        uyy = Image(data=multiply(im2.data, im2.data), **new_image_args).gaussianBlur(**self.gaussian_args).data
        uxy = Image(data=multiply(im1.data, im2.data), **new_image_args).gaussianBlur(**self.gaussian_args).data

        # 官方的cuda python绑定有问题,目前没有修复, 需要用下面的commit才能使用
        # https://github.com/hakaboom/opencv_contrib/commit/ed0a7d567ff4775fc933c889cf856146a3ea79be
        vx = multiply(subtract(multiply(ux, ux), uxx), cov_norm)
        vy = multiply(subtract(multiply(uy, uy), uyy), cov_norm)
        vxy = multiply(subtract(multiply(ux, uy), uxy), cov_norm)

        A1 = add(multiply(multiply(ux, uy), 2), C1)
        A2 = add(multiply(vxy, 2), C2)
        B1 = add(add(pow(ux, 2), pow(uy, 2)), C1)
        B2 = add(add(vx, vy), C2)
        D = multiply(B1, B2)
        S = divide(multiply(A1, A2), D)

        if umat_flag:
            S = S.get()
        elif cuda_flag:
            S = S.download()

        pad = (self.win_size - 1) // 2
        r = Rect(pad, pad, (w - (2 * pad)), (h - (2 * pad)))

        mssim = Image(data=S, dtype=np.float64, place=Place.Ndarray, clone=False).crop(r).data
        mssim = cv2.mean(mssim)[0]

        if full:
            S = np.round(S, 6)  # 精度问题
            return mssim, S * self.data_range
        else:
            return mssim
