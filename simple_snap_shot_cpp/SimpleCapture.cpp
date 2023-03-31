#include "SimpleCapture.h"

#define DLLEXPORT __declspec(dllexport)
extern "C" {
DLLEXPORT void SnapShotInit(LPCWSTR lpClassName, LPCWSTR lpWindowName) {
  SimpleCapture::Singleton()->Initialize({lpClassName, lpWindowName});
}

DLLEXPORT void SnapShot() { SimpleCapture::Singleton()->SnapShot(); }
}