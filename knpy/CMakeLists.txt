cmake_minimum_required(VERSION 3.15)
project(braid_cpp_impl LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(braid_cpp_impl braid.cpp)
install(TARGETS braid_cpp_impl DESTINATION ${CMAKE_CURRENT_LIST_DIR}/.)

add_custom_command(
  TARGET braid_cpp_impl
  POST_BUILD
  COMMAND stubgen -m braid_cpp_impl --include-docstrings -o .)
install(FILES ${CMAKE_BINARY_DIR}/braid_cpp_impl.pyi
  DESTINATION ${CMAKE_CURRENT_LIST_DIR}/.)
