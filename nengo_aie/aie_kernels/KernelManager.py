import importlib_resources
import tempfile
import subprocess
import os

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
    """
    __kernel_sources = {}
    __kernel_objects = {}

    resources = importlib_resources.files(__package__)

    @staticmethod
    def register_kernel_source(opname, *args):
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
                                              "-DNDEBUG", "-c",  # TODO: add support for linking to other objects
                                              source_name, "-o", object_name.name])

            if len(stdout) > 0:
                logger.debug(stdout)

            KernelManager.__kernel_objects[opname] = object_name.name

    @staticmethod
    def get_kernel_object_for(opname):
        """Gets the path to the object file prodiced by the compilation for a given :OpNames: entry.

        Returns
        -------
        A string containing the path to the object file.
        """
        return KernelManager.__kernel_objects[opname]
