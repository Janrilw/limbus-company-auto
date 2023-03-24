import paddle
import paddle.nn as nn
import paddle.nn.functional as F

from baseImage import Image
from baseImage.constant import Place

from typing import Union

def _fspecial_gauss_1d(size, sigma):
    r"""Create 1-D gauss kernel
    Args:
        size (int): the size of gauss kernel
        sigma (float): sigma of normal distribution

    Returns:
        paddle.Tensor: 1D kernel (1 x 1 x size)
    """
    coords = paddle.arange(size, dtype=paddle.float32)
    coords -= size // 2

    g = paddle.exp(-(coords ** 2) / (2 * sigma ** 2))
    g /= g.sum()

    return g.unsqueeze(0).unsqueeze(0)


def gaussian_filter(input, win):
    r""" Blur input with 1-D kernel
    Args:
        input (paddle.Tensor): a batch of tensors to be blurred
        window (paddle.Tensor): 1-D gauss kernel

    Returns:
        paddle.Tensor: blurred tensors
    """
    assert all([ws == 1 for ws in win.shape[1:-1]]), win.shape
    if len(input.shape) == 4:
        conv = F.conv2d
    elif len(input.shape) == 5:
        conv = F.conv3d
    else:
        raise NotImplementedError(input.shape)

    C = input.shape[1]
    out = input
    for i, s in enumerate(input.shape[2:]):
        if s >= win.shape[-1]:
            perms = list(range(win.ndim))
            perms[2 + i] = perms[-1]
            perms[-1] = 2 + i
            out = conv(out, weight=win.transpose(perms), stride=1, padding=0, groups=C)
        else:
            print(
                f"Skipping Gaussian Smoothing at dimension 2+{i} for input: {input.shape} and win size: {win.shape[-1]}"
            )

    return out


def _ssim(X, Y, data_range, win, K=(0.01, 0.03)):
    r""" Calculate ssim index for X and Y

    Args:
        X (paddle.Tensor): images
        Y (paddle.Tensor): images
        win (paddle.Tensor): 1-D gauss kernel
        data_range (float or int, optional): value range of input images. (usually 1.0 or 255)

    Returns:
        paddle.Tensor: ssim results.
    """
    K1, K2 = K
    # batch, channel, [depth,] height, width = X.shape
    compensation = 1.0

    C1 = (K1 * data_range) ** 2
    C2 = (K2 * data_range) ** 2

    win = win.cast(X.dtype)

    mu1 = gaussian_filter(X, win)
    mu2 = gaussian_filter(Y, win)

    mu1_sq = mu1.pow(2)
    mu2_sq = mu2.pow(2)
    mu1_mu2 = mu1 * mu2

    sigma1_sq = compensation * (gaussian_filter(X * X, win) - mu1_sq)
    sigma2_sq = compensation * (gaussian_filter(Y * Y, win) - mu2_sq)
    sigma12 = compensation * (gaussian_filter(X * Y, win) - mu1_mu2)

    cs_map = (2 * sigma12 + C2) / (sigma1_sq + sigma2_sq + C2)  # set alpha=beta=gamma=1
    ssim_map = ((2 * mu1_mu2 + C1) / (mu1_sq + mu2_sq + C1)) * cs_map

    ssim_per_channel = paddle.flatten(ssim_map, 2).mean(-1)
    cs = paddle.flatten(cs_map, 2).mean(-1)
    return ssim_per_channel, cs


def ndarray_to_pd(data):
    return paddle.to_tensor(data.transpose(2, 0, 1)[None, ...], dtype=paddle.float32)


# TODO: 多图的ssim计算
def ssim(
    im1: Image, im2: Image, data_range: int = 255,
    win_size: int = 11, sigma: int = 1.5,
    nonnegative_ssim=False,
) -> Union[int, float]:
    r""" interface of ssim
    Args:
        im1 (paddle.Tensor): a batch of images, (N,C,H,W)
        im2 (paddle.Tensor): a batch of images, (N,C,H,W)
        data_range (float or int, optional): value range of input images. (usually 1.0 or 255)
        win_size: (int, optional): the size of gauss kernel
        sigma: (float, optional): sigma of normal distribution
        nonnegative_ssim (bool, optional): force the ssim response to be nonnegative with relu

    Returns:
        paddle.Tensor: ssim results
    """
    im1 = Image(data=im1, place=Place.Ndarray, dtype=im1.dtype)
    im2 = Image(data=im2, place=Place.Ndarray, dtype=im1.dtype)

    im1 = ndarray_to_pd(im1.data)
    im2 = ndarray_to_pd(im2.data)

    if not im1.shape == im2.shape:
        raise ValueError("Input images should have the same dimensions.")

    for d in range(len(im1.shape) - 1, 1, -1):
        im1 = im1.squeeze(axis=d)
        im2 = im2.squeeze(axis=d)

    if len(im1.shape) not in (4, 5):
        raise ValueError(f"Input images should be 4-d or 5-d tensors, but got {im1.shape}")

    if not im1.type == im2.type:
        raise ValueError("Input images should have the same dtype.")

    if not (win_size % 2 == 1):
        raise ValueError("Window size should be odd.")

    win = _fspecial_gauss_1d(win_size, sigma)
    win = win.tile([im1.shape[1]] + [1] * (len(im1.shape) - 1))

    K = (0.01, 0.03)
    ssim_per_channel, _ = _ssim(im1, im2, data_range=data_range, win=win, K=K)
    if nonnegative_ssim:
        ssim_per_channel = F.relu(ssim_per_channel)

    return ssim_per_channel.mean().item(0)

