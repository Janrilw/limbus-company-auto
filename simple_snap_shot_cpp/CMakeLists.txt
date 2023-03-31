cmake_minimum_required(VERSION 3.0.0)
project(test VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 17)

add_library(simplesnapshot SHARED SimpleCapture.cpp)
