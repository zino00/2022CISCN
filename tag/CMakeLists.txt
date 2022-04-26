cmake_minimum_required(VERSION 3.13)
project(IRHandler VERSION 2.0.0)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -g3 -ggdb3")

set(LT_LLVM_INSTALL_DIR "" CACHE PATH "LLVM installation directory")
list(APPEND CMAKE_PREFIX_PATH "${LT_LLVM_INSTALL_DIR}/lib/cmake/llvm/")

find_package(LLVM 13.0.1 REQUIRED CONFIG)
message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

include_directories(SYSTEM ./tinyxml2 ${LLVM_INCLUDE_DIRS})

# llvm_map_components_to_libnames(llvm_libs all)
llvm_map_components_to_libnames(llvm_libs support core irreader analysis TransformUtils)

# compile tinyxml2 first
add_subdirectory(./tinyxml2)

# then compile IRHandler
add_executable(${PROJECT_NAME} IRHandler.cpp)
target_link_libraries (${PROJECT_NAME} ${llvm_libs} ${CMAKE_SOURCE_DIR}/tinyxml2/libtinyxml2.a)