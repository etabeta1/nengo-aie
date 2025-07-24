from abc import ABC, abstractmethod
import tempfile
import aie.utils.compile as compile_utils  # type: ignore
import subprocess

import logging
logger = logging.getLogger(__name__)


class MlirBuilder(ABC):
    def __init__(self):
        self.__mlir_source = tempfile.NamedTemporaryFile(
            delete=False, suffix=".mlir").name
        self.__xclbin_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=".xclbin").name
        self.__insts_path = tempfile.NamedTemporaryFile(delete=False, suffix=".bin").name

    @abstractmethod
    def build(self, device, size) -> tuple[str, str]:
        pass

    @property
    def mlir_source(self) -> str:
        return self.__mlir_source

    def compile(self) -> tuple[str, str]:
        # We cannot call aiecc.py directly using aie.utils.compile unless we want to make this not working on jupyter (asyncio conflicts)
        output = subprocess.check_output(["aiecc.py",
                                          "--aie-generate-xclbin", "--no-compile-host", f"--xclbin-name={self.__xclbin_path}",
                                          "--no-xchesscc", "--no-xbridge",
                                          "--aie-generate-npu-insts", f"--npu-insts-name={self.__insts_path}",
                                          self.__mlir_source
                                         ],
                                         stderr=subprocess.STDOUT)

        if len(output) > 0:
            logger.debug(output)

        return (self.__insts_path, self.__xclbin_path)
