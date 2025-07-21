#!/usr/bin/env python3

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import subprocess
import os
import sys

KERNEL_FOLDER = "./nengo_aie/aie_kernels"
LIBNENGOAIE_FOLDER = "./nengo_aie/libnengoaie"
MLIR_AIE_PATH = "/notebooks/mlir-aie"

def getAllKernelDirs():
    dirs = os.listdir(KERNEL_FOLDER)
    dirs = [os.path.join(KERNEL_FOLDER, d) for d in dirs]
    dirs = [d for d in dirs if os.path.isdir(d)]
    dirs = [d for d in dirs if os.path.exists(os.path.join(d, "kernel.cc"))]
    return dirs

def _build():
    print("[BUILD]:", "Building kernels...")
    peano_path = os.environ.get("PEANO_INSTALL_DIR")

    if not peano_path:
        raise ArrtibuteError("ERROR: env variable $PEANO_INSTALL_DIR not set")

    dirs = getAllKernelDirs()
    
    for d in dirs:
        print("[BUILD]:", "building", d.split(":")[-1])
        
        subprocess.check_call([peano_path + "/bin/clang++", "-O2", "-std=c++20", "--target=aie2-none-unknown-elf",
                              "-Wno-parentheses", "-Wno-attributes", "-Wno-macro-redefined", "-Wno-empty-body",
                              "-DNDEBUG", "-c",
                              "-I", "/home/mliraie/mlir-aie/ironenv/lib/python3.12/site-packages/mlir_aie/include",
                              os.path.join(d, "kernel.cc"), "-o", os.path.join(d, "kernel.o")])
    
    print("[BUILD]:", "Building libnengoaie...")
    subprocess.check_call(['cmake', '.', '-DMLIR_AIE_PATH=' + MLIR_AIE_PATH, '-DTARGET_NAME=aie2', '-Wno-dev'], cwd=LIBNENGOAIE_FOLDER)
    subprocess.check_call(['cmake', '--build', '.', '--config', 'Release'], cwd=LIBNENGOAIE_FOLDER)

def _clean():
    print("[CLEAN]:", "Kernels")
    
    dirs = getAllKernelDirs()

    for d in dirs:
        print("[CLEAN]:", d.split(":")[-1])
        subprocess.check_call(["rm", "-f", os.path.join(d, "kernel.o")])

    print("[CLEAN]:", "libnengoaie")
    
    subprocess.check_call(['make', 'clean'], cwd=LIBNENGOAIE_FOLDER)

targets = {
    "build": _build,
    "clean": _clean
}

if __name__ == "__main__":
    target_name = sys.argv[1]
    if target_name in targets.keys():
        targets[target_name]()
    else:
        print(f"No target found for '{target_name}', available targets: {targets.keys()}")
        
    