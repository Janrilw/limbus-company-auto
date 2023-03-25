import PIL.Image
import numpy as np
import win32com.client
import win32gui, win32ui, win32con, win32api
from PIL import Image, ImageGrab
import time

def screen_capture(filename, hwnd):
    """全屏截图尝试"""
    hwnd = 0  # 窗口的编号，0号表示当前活跃窗口

    # 根据窗口句柄获取窗口的设备上下文DC(Divice Context)
    hwndDC = win32gui.GetWindowDC(hwnd)
    # 根据窗口的DC获取mfcDC
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    # mfcDC创建可兼容的DC
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建bigmap准备保存图片
    saveBitMap = win32ui.CreateBitmap()
    # 获取监控器信息
    MoniterDev = win32api.EnumDisplayMonitors(None, None)
    print(MoniterDev)
    w = MoniterDev[0][2][2]
    h = MoniterDev[0][2][3]
    # print w,h　　　#图片大小
    # 为bitmap开辟空间
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    # 高度saveDC，将截图保存到saveBitmap中
    saveDC.SelectObject(saveBitMap)
    # 截取从左上角(0，0)长宽为(w，h)的图片
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC, filename)


def EnumWindows():
    ret = dict()

    def _get_all_hwnd(hwnd, mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            txt = win32gui.GetWindowText(hwnd)
            if len(txt) > 0:
                ret.update({hwnd: txt})

    win32gui.EnumWindows(_get_all_hwnd, 0)
    return ret


# def FindWindow(by_title):
#     ws = EnumWindows()
#     hwnd = None
#     for k in ws:
#         if by_title == ws[k]:
#             hwnd = k
#             break
#     if hwnd is not None:
#         # if hwnd!=win32gui.GetForegroundWindow():
#         #     shell=win32com.client.Dispatch('WScript.Shell')
#         #     shell.SendKeys('%')
#         #     win32gui.SetForegroundWindow(hwnd)
#
#         r = win32gui.GetWindowRect(hwnd)
#
#         hwin = win32gui.GetDesktopWindow()
#         left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
#         top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
#
#         # 根据窗口句柄获取窗口的设备上下文DC(Divice Context)
#         hwndDC = win32gui.GetWindowDC(hwnd)
#         # 根据窗口的DC获取mfcDC
#         mfcDC = win32ui.CreateDCFromHandle(hwndDC)
#         # mfcDC创建可兼容的DC
#         saveDC = mfcDC.CreateCompatibleDC()
#         # 创建bigmap准备保存图片
#         saveBitMap = win32ui.CreateBitmap()
#
#         # 为bitmap开辟空间
#         saveBitMap.CreateCompatibleBitmap(mfcDC, r[2] - r[0], r[3] - r[1])
#         # 高度saveDC，将截图保存到saveBitmap中
#         saveDC.SelectObject(saveBitMap)
#         # 截取从左上角(0，0)长宽为(w，h)的图片
#         saveDC.BitBlt((left, top), (r[2] - left, r[3] - top), mfcDC, (left, top), win32con.SRCCOPY)
#         saveBitMap.SaveBitmapFile(saveDC, 's1.png')
#         im = Image.open('s1.png')
#         im = im.convert('RGB')
#         im.save('s1.png')


def get_window_pos(name):
    name = name
    handle = win32gui.FindWindow(0, name)
    if handle == 0:
        return None
    else:
        return win32gui.GetWindowRect(handle)


offset = (8, 31, -8, -8)
from baseImage import Image as Image2


def window_capture(name, show=False, save=None):
    x1, y1, x2, y2 = get_window_pos(name)
    handle = win32gui.FindWindow(0, name)
    win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
    win32gui.SetForegroundWindow(handle)
    time.sleep(0.1)

    img_ready = ImageGrab.grab((x1 + 8, y1 + 31, x2 - 8, y2 - 8))

    if show:
        img_ready.show()
    if save:
        img_ready.save(save)
    img_ready.save('tmp.bmp')
    return Image2('tmp.bmp'),x1, y1
    # return np.asarray(img_ready)


if __name__ == '__main__':
    # FindWindow('微信')
    pass
    window_capture('LimbusCompany', show=True)

    # ws=EnumWindows()
    # hwnd=0
    # for w in ws:
    #     print(w,ws[w])
    #     if 'LimbusCompany' in ws[w]:
    #         hwnd=w
    #
    # beg = time.time()
    # screen_capture("ss.jpg",hwnd)
    #
    # end = time.time()
    #
    # print(end - beg)
