#pragma once

#include "utils.h"

#pragma comment(lib, "dxgi.lib")
#pragma comment(lib, "d3d11.lib")
#pragma comment(lib, "Dwmapi.lib")

class SimpleWindow {
  struct Window {
    HWND hwnd;
    std::wstring class_name;
    std::wstring title;
    RECT rect;
  };

public:
  SimpleWindow() = default;
  SimpleWindow(LPCWSTR lpClassName, LPCWSTR lpWindowName) {
    // get hwnd
    _window.hwnd = FindWindowW(lpClassName, lpWindowName);

    // get class name
    auto class_name_length = 256;
    std::wstring class_name(class_name_length, 0);
    GetClassNameW(_window.hwnd, class_name.data(), class_name_length);
    _window.class_name = std::move(class_name);

    // get title
    auto title_length = GetWindowTextLengthW(_window.hwnd) + 1;
    std::wstring title(title_length, 0);
    GetWindowTextW(_window.hwnd, title.data(), title_length);
    _window.title = std::move(title);

    // get rect
    SetProcessDPIAware();
    GetWindowRect(_window.hwnd, &_window.rect);
  }
  HWND GetHWND() { return _window.hwnd; }
  auto GetWidth() { return _window.rect.right - _window.rect.left; }
  auto GetHeight() { return _window.rect.bottom - _window.rect.top; }

private:
  Window _window;
};

class SimpleCapture {
  friend class SimpleWindow;
  typedef winrt::Windows::Graphics::DirectX::Direct3D11::IDirect3DDevice
      IDirect3DDevice;
  typedef winrt::Windows::Graphics::Capture::GraphicsCaptureItem
      GraphicsCaptureItem;
  typedef winrt::Windows::Graphics::Capture::Direct3D11CaptureFramePool
      Direct3D11CaptureFramePool;
  typedef winrt::Windows::Graphics::Capture::GraphicsCaptureSession
      GraphicsCaptureSession;
  typedef winrt::Windows::Graphics::DirectX::DirectXPixelFormat
      DirectXPixelFormat;
  typedef winrt::Windows::Graphics::SizeInt32 SizeInt32;

public:
  SimpleCapture() = default;
  SimpleCapture(SimpleWindow window) { Initialize(window); }
  ~SimpleCapture() {}
  void Initialize(SimpleWindow window) {
    // 初始化d3d设备和上下文
    D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr,
                      D3D11_CREATE_DEVICE_BGRA_SUPPORT, nullptr, 0,
                      D3D11_SDK_VERSION, _d3d11_device.put(), nullptr,
                      _d3d11_device_context.put());
    _window = window;
    // 通过d3d设备获取对应的dxgi设备
    auto dxgi_device = _d3d11_device.as<IDXGIDevice>();
    // 通过dxgi设备获取对应的IDirect3DDevice设备
    _device = util::CreateDirect3DDevice(dxgi_device.get());
    // 获取窗口的size（包括标题栏）
    _size = winrt::Windows::Graphics::SizeInt32{_window.GetWidth(),
                                                _window.GetHeight()};
    // 判断窗口是否全屏
    QUERY_USER_NOTIFICATION_STATE pquns;
    SHQueryUserNotificationState(&pquns);
    if (pquns != QUNS_RUNNING_D3D_FULL_SCREEN) {
      _full_screen = false;
      // 这一部分是 copy 的 obs 的代码，具体逻辑可以查看相应源码
      util::GetClientBox(_window.GetHWND(), _window.GetWidth(),
                         _window.GetHeight(), &_client_box);
    }
  }

  static SimpleCapture *Singleton() {
    static SimpleCapture single;
    return &single;
  }

  static void SingletonInit(LPCWSTR lpClassName, LPCWSTR lpWindowName) {
    Singleton()->Initialize({lpClassName, lpWindowName});
  }

  static void SingletonSnapShot() { Singleton()->SnapShot(); }

  void SnapShot() {
    // 通过 hwnd 获取对应的 GraphicsCaptureItem
    _item = util::CreateCaptureItemForWindow(_window.GetHWND());
    // 通过 IDirect3DDevice 设备创建帧池
    _frame_pool =
        Direct3D11CaptureFramePool::Create(_device, _pixel_format, 2, _size);
    // 创建 GraphicsCaptureItem 对象对应的会话
    _session = _frame_pool.CreateCaptureSession(_item);
    // 禁用截图时的鼠标显示
    _session.IsCursorCaptureEnabled(false);
    auto is_frame_arrived = false;
    winrt::Windows::Graphics::Capture::Direct3D11CaptureFrame frame = nullptr;
    // 注册帧池回调函数
    _frame_pool.FrameArrived([&](auto &frame_pool, auto &) {
      if (is_frame_arrived)
        return;
      frame = frame_pool.TryGetNextFrame();
      is_frame_arrived = true;
      return;
    });
    // 开启会话捕获
    _session.StartCapture();

    // Message pump
    MSG msg;
    while (!is_frame_arrived) {
      if (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE) > 0)
        DispatchMessage(&msg);
    }

    // 释放会话和帧池资源
    _session.Close();
    _frame_pool.Close();

    // 不清楚作用，判断是将帧中数据转为 ID3D11Texture2D 格式
    winrt::com_ptr<ID3D11Texture2D> texture =
        util::GetDXGIInterfaceFromObject<ID3D11Texture2D>(frame.Surface());

    winrt::com_ptr<ID3D11Texture2D> user_texture;
    UINT width, height;
    D3D11_TEXTURE2D_DESC desc{};
    texture->GetDesc(&desc);
    if (!_full_screen) { // 窗口模式处理
      // 对前面的 texture 进行 copy，具体原理不清楚（反正能跑就行）
      user_texture = util::CopyD3DTextureClient(_d3d11_device, texture,
                                                &_client_box, true);
      // 设置图像的宽高
      width = _client_box.right - _client_box.left;
      height = _client_box.bottom - _client_box.top;
    } else { // 全屏模式处理
      user_texture = util::CopyD3DTexture(_d3d11_device, texture, true);
      width = desc.Width;
      height = desc.Height;
    }

    // 进行map映射，从这开始就没注释了，原理大概就是将图像数据编码成bitmap吧（大概）
    D3D11_MAPPED_SUBRESOURCE resource;
    winrt::check_hresult(_d3d11_device_context->Map(
        user_texture.get(), NULL, D3D11_MAP_READ, 0, &resource));

    BITMAPINFO lBmpInfo;

    // BMP 32 bpp
    ZeroMemory(&lBmpInfo, sizeof(BITMAPINFO));
    lBmpInfo.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    lBmpInfo.bmiHeader.biBitCount = 32;
    lBmpInfo.bmiHeader.biCompression = BI_RGB;
    lBmpInfo.bmiHeader.biWidth = width;
    lBmpInfo.bmiHeader.biHeight = height;
    lBmpInfo.bmiHeader.biPlanes = 1;
    lBmpInfo.bmiHeader.biSizeImage = width * height * 4;

    std::unique_ptr<BYTE> pBuf(new BYTE[lBmpInfo.bmiHeader.biSizeImage]);
    UINT lBmpRowPitch = width * 4;
    auto sptr = static_cast<BYTE *>(resource.pData);
    auto dptr = pBuf.get() + lBmpInfo.bmiHeader.biSizeImage - lBmpRowPitch;

    UINT lRowPitch = std::min<UINT>(lBmpRowPitch, resource.RowPitch);

    for (size_t h = 0; h < height; ++h) {
      memcpy_s(dptr, lBmpRowPitch, sptr, lRowPitch);
      sptr += resource.RowPitch;
      dptr -= lBmpRowPitch;
    }

    // Save bitmap buffer into the file ScreenShot.bmp
    WCHAR lMyDocPath[MAX_PATH];

    winrt::check_hresult(SHGetFolderPathW(nullptr, CSIDL_PERSONAL, nullptr,
                                          SHGFP_TYPE_CURRENT, lMyDocPath));

    FILE *lfile = nullptr;

    if (auto lerr = _wfopen_s(&lfile, _lFilePath.c_str(), L"wb"); lerr != 0)
      return;

    if (lfile != nullptr) {
      BITMAPFILEHEADER bmpFileHeader;

      bmpFileHeader.bfReserved1 = 0;
      bmpFileHeader.bfReserved2 = 0;
      bmpFileHeader.bfSize = sizeof(BITMAPFILEHEADER) +
                             sizeof(BITMAPINFOHEADER) +
                             lBmpInfo.bmiHeader.biSizeImage;
      bmpFileHeader.bfType = 'MB';
      bmpFileHeader.bfOffBits =
          sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

      fwrite(&bmpFileHeader, sizeof(BITMAPFILEHEADER), 1, lfile);
      fwrite(&lBmpInfo.bmiHeader, sizeof(BITMAPINFOHEADER), 1, lfile);
      fwrite(pBuf.get(), lBmpInfo.bmiHeader.biSizeImage, 1, lfile);

      fclose(lfile);
    }

    return;
  }

private:
  std::wstring _lFilePath = L"ScreenShot.bmp";
  bool _init = false;
  bool _full_screen = true;
  SimpleWindow _window;
  winrt::com_ptr<ID3D11Device> _d3d11_device = nullptr;
  winrt::com_ptr<ID3D11DeviceContext> _d3d11_device_context = nullptr;
  D3D11_BOX _client_box;
  IDirect3DDevice _device = nullptr;
  GraphicsCaptureItem _item = nullptr;
  SizeInt32 _size;
  DirectXPixelFormat _pixel_format = DirectXPixelFormat::B8G8R8A8UIntNormalized;
  Direct3D11CaptureFramePool _frame_pool = nullptr;
  GraphicsCaptureSession _session = nullptr;
};