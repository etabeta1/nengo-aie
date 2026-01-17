import importlib
import tempfile
import subprocess
import os
import shutil
from pathlib import Path
from . import OpNames

import logging
logger = logging.getLogger(__name__)


class KernelManager:
    """Manages the compilation and the tracking of all the sources and compilation artifacts related to each kernel.

    Attributes
    ----------
    __kernel_sources : dict[OpNames, str]
        Tracks the position of the .cc source for each kernel.
    __kernel_objects : dict[OpNames, str]
        Tracks the position of the object file for each kernel.
    __inc_folders : list[str]
        Traks all the externally registered folders containing headers used in the kernels.
    """
    __kernel_sources = {}
    __kernel_objects = {}
    __inc_folders = []

    resources = importlib.resources.files(__package__)

    @staticmethod
    def register_kernel_source(opname: OpNames, *args):
        """Registers a new source file for a given :OpNames: entry.

        Returns early without mutating the state of the class if a kernel has already been registered.

        Parameters
        ----------
        opname : OpNames
            The :OpNames: entry associated to the kernel whose sources are to be registered.
        *args : str[]
            Path to the .cc source, one folder at a time (e.g. `register_kernel_source(..., "path", "to", "source.cc")`).
        """
        if opname in KernelManager.__kernel_sources.keys():
            logger.debug(f"{opname.value} kernel already registered")
            return

        logger.debug(f"Registering {opname.value} kernel")
        source_content = KernelManager.resources.joinpath(*args).read_bytes()
        destination = tempfile.NamedTemporaryFile(delete=False, suffix=".cc")

        with open(destination.name, "wb") as f:
            f.write(source_content)

        KernelManager.__kernel_sources[opname] = destination.name

    # Warning: this method has been vibe-coded, handle with care
    @staticmethod
    def register_inc_folder(*args):
        resource = KernelManager.resources.joinpath(*args)

        logger.debug(f"Registering {args[-1]} include folder")

        temp_dir = tempfile.TemporaryDirectory(delete=False)
        KernelManager.__inc_folders.append(temp_dir.name)

        dst = Path(temp_dir.name) / resource.name

        with importlib.resources.as_file(resource) as src:
            shutil.copytree(src, dst, dirs_exist_ok=True)

    @staticmethod
    def compile_all():
        """Compiles all the registered kernel sources into object files (one for each source).
        """
        logger.info("Compiling kernels")

        peano_path = os.environ.get("PEANO_INSTALL_DIR")

        if not peano_path:
            raise AttributeError("ERROR: env variable $PEANO_INSTALL_DIR not set")

        for opname, source_name in KernelManager.__kernel_sources.items():
            logger.debug(f"Compiling {opname.value} kernel")

            object_name = tempfile.NamedTemporaryFile(delete=False, suffix=".o")

            stdout = subprocess.check_output([f"{peano_path}/bin/clang++", "-O2", "-std=c++20", "--target=aie2-none-unknown-elf",
                                              "-Wno-parentheses", "-Wno-attributes", "-Wno-macro-redefined", "-Wno-empty-body",
                                              "-I", "/home/mliraie/mlir-aie/ironenv/lib/python3.12/site-packages/mlir_aie/include",
                                              "-DNDEBUG", "-c",
                                              *[f"-I{i}" for i in KernelManager.__inc_folders],
                                              source_name, "-o", object_name.name])

            if len(stdout) > 0:
                logger.debug(stdout)

            KernelManager.__kernel_objects[opname] = object_name.name

    @staticmethod
    def get_kernel_object_for(opname: OpNames) -> str:
        """Gets the path to the object file prodiced by the compilation for a given :OpNames: entry.

        Returns
        -------
        A string containing the path to the object file.
        """
        return KernelManager.__kernel_objects[opname]
