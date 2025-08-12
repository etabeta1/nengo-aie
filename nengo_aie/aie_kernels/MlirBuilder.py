from abc import ABC, abstractmethod
import tempfile
import aie.utils.compile as compile_utils  # type: ignore
from aie.iron.resolvable import Resolvable  # type: ignore
import subprocess

import logging
logger = logging.getLogger(__name__)


class MlirBuilder(ABC):
    """Base class for every class that needs to build and compile MLIR modules.

    Attributes
    ----------
    __mlir_source : str
        Path to the file containing the output of the MLIR module generation.
    __xclbin_path : str
        Path to the xclbin file.
    __insts_path : str
        Path to the insts file.

    Properties
    ----------
    mlir_source : str
        Path to the file containing the output of the MLIR module generation.

    Methods
    -------
    build(device, size), abstract
        Describes the MLIR module.
    compile()
        Calls aiecc.py to compile the MLIR module.
    """

    def __init__(self):
        # TODO: delete temp files when the program ends.
        self.__mlir_source = tempfile.NamedTemporaryFile(
            delete=False, suffix=".mlir").name
        self.__xclbin_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=".xclbin").name
        self.__insts_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=".bin").name

    @abstractmethod
    def build(self, device: Resolvable, size: int) -> tuple[str, str]:
        """Writes the MLIR module to a temp file, compiles it and returns a tuple containing the path to the file containing the instructions and the path to the xclbin.

        Parameters
        ----------
        device : xrt.device
            The device this module is ging to be uploaded to.
        size : int
            The size of each one of the input vectors (should be a multiple of 16).

        Returns
        -------
        A tuple containing the path to the file containing the instructions and the path to the xclbin.
        """

        pass

    @property
    def mlir_source(self) -> str:
        return self.__mlir_source

    def compile(self) -> tuple[str, str]:
        """Compiles the MLIR module into an xclbin and an insts file.

        Returns
        -------
        A tuple containing the path to the file containing the instructions and the path to the xclbin.
        """

        # We cannot call aiecc.py directly using aie.utils.compile unless we want to break the library in jupyter (asyncio conflicts)
        try:
            output = subprocess.check_output(["aiecc.py",
                                              "--aie-generate-xclbin", "--no-compile-host", f"--xclbin-name={self.__xclbin_path}",
                                              "--no-xchesscc", "--no-xbridge",
                                              "--aie-generate-npu-insts", f"--npu-insts-name={self.__insts_path}",
                                              self.__mlir_source
                                              ],
                                             cwd=tempfile.gettempdir(),
                                             stderr=subprocess.STDOUT)

            if len(output) > 0:
                logger.debug(output)
        except subprocess.CalledProcessError as e:
            logger.exception(e.output.decode())
            raise e

        return (self.__insts_path, self.__xclbin_path)
