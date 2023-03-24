import numpy as np
import numpy.typing as npt

Dtype = npt.DTypeLike

def check_file(file_name: str) -> bool: ...


def check_image_valid(image: np.ndarray) -> bool: ...


def read_image(filename: str, flags: int) -> np.ndarray: ...


def bytes_2_img(byte: bytes) -> np.ndarray: ...


def npType_to_cvType(dtype: Dtype, channels: int) -> int: ...


def cvType_to_npType(dtype: int, channels: int) -> Dtype: ...


class AutoIncrement(object): ...