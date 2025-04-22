cmake_minimum_required(VERSION 3.1...3.26)

# Declare MLIR_AIE_PATH as a cached variable if not defined.
if(NOT DEFINED MLIR_AIE_PATH)
  set(MLIR_AIE_PATH "" CACHE PATH "Path to the mlir-aie repository")
endif()
if(MLIR_AIE_PATH STREQUAL "")
  message(FATAL_ERROR "MLIR_AIE_PATH is empty. Set it with -DMLIR_AIE_PATH=/path/to/mlir-aie")
endif()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED YES)

find_program(WSL NAMES powershell.exe)

if (NOT WSL)
    set(CMAKE_C_COMPILER gcc-13)
    set(CMAKE_CXX_COMPILER g++-13)
    set(BOOST_ROOT /usr/include/boost CACHE STRING "Path to Boost install")
    set(XRT_INC_DIR /opt/xilinx/xrt/include CACHE STRING "Path to XRT cloned repo")
    set(XRT_LIB_DIR /opt/xilinx/xrt/lib CACHE STRING "Path to xrt_coreutil.lib")
else()
    set(BOOST_ROOT C:/Technical/thirdParty/boost_1_83_0 CACHE STRING "Path to Boost install")
    set(XRT_INC_DIR C:/Technical/XRT/src/runtime_src/core/include CACHE STRING "Path to XRT cloned repo")
    set(XRT_LIB_DIR C:/Technical/xrtNPUfromDLL CACHE STRING "Path to xrt_coreutil.lib")
endif()

set(TARGET_NAME test CACHE STRING "Target name to be built")
set(ProjectName ${TARGET_NAME})
set(currentTarget ${TARGET_NAME})

if (WSL)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR})
endif()

project(${ProjectName})

# Find Boost
find_package(Boost REQUIRED)

# Set runtime library path using MLIR_AIE_PATH
set(RUNTIME_LIB_PATH "${MLIR_AIE_PATH}/runtime_lib/test_lib")
message(STATUS "MLIR_AIE_PATH = ${MLIR_AIE_PATH}")
message(STATUS "RUNTIME_LIB_PATH = ${RUNTIME_LIB_PATH}")


add_executable(${currentTarget}
    "${CMAKE_CURRENT_SOURCE_DIR}/libnengoaie.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/test.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/utils.cpp"
)

target_compile_definitions(${currentTarget} PUBLIC 
    DISABLE_ABI_CHECK=1
)

target_include_directories(${currentTarget} PUBLIC 
    ${XRT_INC_DIR}
    ${Boost_INCLUDE_DIRS}
    ${RUNTIME_LIB_PATH}
)

target_link_directories(${currentTarget} PUBLIC
    ${XRT_LIB_DIR}
    ${Boost_LIBRARY_DIRS}
)

if (NOT WSL)
    target_link_libraries(${currentTarget} PUBLIC
        xrt_coreutil
        boost_program_options
        boost_filesystem
    )
else()
    target_link_libraries(${currentTarget} PUBLIC
        xrt_coreutil
    )
endif()