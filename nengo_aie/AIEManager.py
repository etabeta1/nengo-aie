import pyxrt as xrt  # type: ignore
import aie.utils.xrt as xrt_utils  # type: ignore

import logging
logger = logging.getLogger(__name__)


class AIEManager:

    @staticmethod
    def init_aie(xclbin_path) -> tuple[xrt.device, xrt.kernel]:
        device = xrt.device(0)
        xclbin = xrt.xclbin(xclbin_path)
        xkernel = xclbin.get_kernels()[0]
        device.register_xclbin(xclbin)
        context = xrt.hw_context(device, xclbin.get_uuid())
        kernel = xrt.kernel(context, xkernel.get_name())

        return (device, kernel)

    @staticmethod
    def load_insts(insts_path, device, kernel) -> tuple[list[int], xrt.bo]:
        insts_v = xrt_utils.read_insts(insts_path)
        insts_bo = xrt.bo(device, len(insts_v) * 4,
                          xrt.bo.cacheable, kernel.group_id(1))
        insts_bo.write(insts_v, 0)
        insts_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

        return (insts_v, insts_bo)


class AIEContext:
    def __init__(self, device, kernel, instr_v, instr_bo):
        self.__device = device
        self.__kernel = kernel
        self.__instr_v = instr_v
        self.__instr_bo = instr_bo
        self.__bos = {}
        self.__next_gid = 3

    def create_inout_bo(self, name, size):
        bo = xrt.bo(self.__device, size, xrt.bo.host_only,
                    self.__kernel.group_id(self.__next_gid))
        self.__next_gid += 1
        self.__bos[name] = bo

        return bo

    def get_bo(self, name):
        return self.__bos[name]

    def kernel_call(self, *args):
        h = self.__kernel(3, self.__instr_bo, len(self.__instr_v), *args)
        h.wait()
