#pragma once

#include <d3d11.h>
#include <dwmapi.h>
#include <dxgi.h>
#include <roerrorapi.h>
#include <shlobj_core.h>
#include <windows.graphics.capture.interop.h>
#include <windows.graphics.directx.direct3d11.interop.h>
#include <windows.h>
#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.Graphics.Capture.h>
#include <winrt/Windows.System.h>
#include <winrt/base.h>
#include <winrt/windows.graphics.directx.direct3d11.h>

namespace util {

inline auto CreateCaptureItemForWindow(HWND hwnd) {
  using namespace winrt::Windows::Graphics::Capture;
  auto interop_factory =
      winrt::get_activation_factory<GraphicsCaptureItem,
                                    IGraphicsCaptureItemInterop>();
  GraphicsCaptureItem item = nullptr;
  winrt::check_hresult(interop_factory->CreateForWindow(
      hwnd, winrt::guid_of<IGraphicsCaptureItem>(), winrt::put_abi(item)));
  return item;
}

inline auto CreateDirect3DDevice(IDXGIDevice *dxgi_device) {
  using namespace winrt::Windows::Graphics::DirectX::Direct3D11;
  winrt::com_ptr<::IInspectable> d3d_device;
  winrt::check_hresult(
      CreateDirect3D11DeviceFromDXGIDevice(dxgi_device, d3d_device.put()));
  return d3d_device.as<IDirect3DDevice>();
}

template <typename T>
auto GetDXGIInterfaceFromObject(
    winrt::Windows::Foundation::IInspectable const &object) {
  auto access = object.as<
      Windows::Graphics::DirectX::Direct3D11::IDirect3DDxgiInterfaceAccess>();
  winrt::com_ptr<T> result;
  winrt::check_hresult(
      access->GetInterface(winrt::guid_of<T>(), result.put_void()));
  return result;
}

inline auto CopyD3DTexture(winrt::com_ptr<ID3D11Device> const &device,
                           winrt::com_ptr<ID3D11Texture2D> const &texture,
                           bool asStagingTexture) {
  winrt::com_ptr<ID3D11DeviceContext> context;
  device->GetImmediateContext(context.put());

  D3D11_TEXTURE2D_DESC desc = {};
  texture->GetDesc(&desc);
  // Clear flags that we don't need
  desc.Usage = asStagingTexture ? D3D11_USAGE_STAGING : D3D11_USAGE_DEFAULT;
  desc.BindFlags = asStagingTexture ? 0 : D3D11_BIND_SHADER_RESOURCE;
  desc.CPUAccessFlags = asStagingTexture ? D3D11_CPU_ACCESS_READ : 0;
  desc.MiscFlags = 0;

  // Create and fill the texture copy
  winrt::com_ptr<ID3D11Texture2D> texture_copy = nullptr;
  winrt::check_hresult(
      device->CreateTexture2D(&desc, nullptr, texture_copy.put()));
  context->CopyResource(texture_copy.get(), texture.get());
  return texture_copy;
}

inline auto CopyD3DTextureClient(winrt::com_ptr<ID3D11Device> const &device,
                                 winrt::com_ptr<ID3D11Texture2D> const &texture,
                                 D3D11_BOX *client_box, bool asStagingTexture) {
  winrt::com_ptr<ID3D11DeviceContext> context;
  device->GetImmediateContext(context.put());

  D3D11_TEXTURE2D_DESC desc = {};
  texture->GetDesc(&desc);
  // Clear flags that we don't need
  desc.Usage = asStagingTexture ? D3D11_USAGE_STAGING : D3D11_USAGE_DEFAULT;
  desc.BindFlags = asStagingTexture ? 0 : D3D11_BIND_SHADER_RESOURCE;
  desc.CPUAccessFlags = asStagingTexture ? D3D11_CPU_ACCESS_READ : 0;
  desc.MiscFlags = 0;

  // Create and fill the texture copy
  winrt::com_ptr<ID3D11Texture2D> texture_copy = nullptr;
  winrt::check_hresult(
      device->CreateTexture2D(&desc, nullptr, texture_copy.put()));
  context->CopySubresourceRegion(texture_copy.get(), 0, 0, 0, 0, texture.get(),
                                 0, client_box);
  return texture_copy;
}

inline bool GetClientBox(HWND window, UINT width, UINT height,
                         D3D11_BOX *client_box) {
  RECT client_rect{}, window_rect{};
  POINT upper_left{};

  /* check iconic (minimized) twice, ABA is very unlikely */
  bool client_box_available =
      !IsIconic(window) && GetClientRect(window, &client_rect) &&
      !IsIconic(window) && (client_rect.right > 0) &&
      (client_rect.bottom > 0) &&
      (DwmGetWindowAttribute(window, DWMWA_EXTENDED_FRAME_BOUNDS, &window_rect,
                             sizeof(window_rect)) == S_OK) &&
      ClientToScreen(window, &upper_left);
  if (client_box_available) {
    const uint32_t left = (upper_left.x > window_rect.left)
                              ? (upper_left.x - window_rect.left)
                              : 0;
    client_box->left = left;

    const uint32_t top =
        (upper_left.y > window_rect.top) ? (upper_left.y - window_rect.top) : 0;
    client_box->top = top;

    uint32_t texture_width = 1;
    if (width > left) {
      texture_width = min(width - left, (uint32_t)client_rect.right);
    }

    uint32_t texture_height = 1;
    if (height > top) {
      texture_height = min(height - top, (uint32_t)client_rect.bottom);
    }

    client_box->right = left + texture_width;
    client_box->bottom = top + texture_height;

    client_box->front = 0;
    client_box->back = 1;

    client_box_available =
        (client_box->right <= width) && (client_box->bottom <= height);
  }

  return client_box_available;
}
} // namespace util
