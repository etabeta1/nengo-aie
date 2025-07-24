from abc import ABC, abstractmethod
import tempfile
import aie.utils.compile as compile_utils


class MlirBuilder(ABC):
    def __init__(self):
        self.__mlir_source = tempfile.NamedTemporaryFile(delete=False, suffix=".mlir").name
        self.__xclbin_path = tempfile.NamedTemporaryFile(delete=False, suffix=".xclbin").name
        self.__insts_path = tempfile.NamedTemporaryFile(delete=False).name

    @abstractmethod
    def build(self, device, size):
        pass

    @property
    def mlir_source(self):
        return __mlir_source

    def compile(self):
        compile_utils.compile_mlir_module_to_binary(self.__mlir_source, self.__insts_path, self.__xclbin_path)

        return (self.__insts_path, self.__xclbin_path)