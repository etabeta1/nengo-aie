import pyxrt as xrt  # type: ignore
import aie.utils.xrt as xrt_utils  # type: ignore
import math

import logging
logger = logging.getLogger(__name__)


class AIEManager:
    """Utility class used to upload code to the NPU.

    Methods
    -------
    init_aie(xclbin_path) : tuple[xrt.device, xrt.kernel]
        Registers an xclbin to the first NPU device installed.
    load_insts(insts_path, device, kernel) : tuple[list[int], xrt.bo]
        Load and sync insts to the NPU.
    next_multiple_of(divider) : 
        Returns a function (int -> int) that returns the parameter rounded to the next multiple of :divider:.
    """

    @staticmethod
    def init_aie(xclbin_path) -> tuple[xrt.device, xrt.kernel]:
        """Registers an xclbin to the first NPU device installed.

        Parameters
        ----------
        xclbin_path : str
            Path to the xclbin file.

        Returns
        -------
        A tuple containing a reference to the programmed device and the callable kernel.
        """
        device = xrt.device(0)
        xclbin = xrt.xclbin(xclbin_path)
        xkernel = xclbin.get_kernels()[0]
        device.register_xclbin(xclbin)
        context = xrt.hw_context(device, xclbin.get_uuid())
        kernel = xrt.kernel(context, xkernel.get_name())

        return (device, kernel)

    @staticmethod
    def load_insts(insts_path, device, kernel) -> tuple[list[int], xrt.bo]:
        """Load instructions to the NPU.

        Parameters
        ----------
        insts_path : str
            Path to the insts file.
        device : xrt.device
            The device to be programmed.
        kernel : xrt.kernel
            The callable kernel from which instantiate the group_id

        Returns
        -------
        A tuple containing the list of instructions loaded to the npu and the related buffer object.
        """
        insts_v = xrt_utils.read_insts(insts_path)
        insts_bo = xrt.bo(device, len(insts_v) * 4,
                          xrt.bo.cacheable, kernel.group_id(1))
        insts_bo.write(insts_v, 0)
        insts_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

        return (insts_v, insts_bo)

    @staticmethod
    def next_multiple_of(divider):
        return lambda x: divider * math.ceil(x / divider)


class AIEContext:
    """Record class used to encapsulate all the necessary information to call and allocate buffer objects.

    Attributes
    ----------
    __device : xrt.device
        Reference to the NPU device.
    __kernel : xrt.kernel
        Callable kernel.
    __instr_v : list[int]
        List of all the instructions loaded into the NPU.
    __instr_bo : xrt.bo
        Buffer object associated to the instructions.
    __bos : dict[str, xrt.bo]
        All the buffers allocated with their names.
    __next_gid : int
        Used to create buffer objects with incremental group_id.

    Methods
    -------
    create_inout_bo(name, volume, itemsize) : xrt.bo
        Creates a buffer HOST_ONLY buffer object.
    kernel_call(*args) : xrt.ert_cmd_state
        Calls the kernel on the NPU.
    """

    def __init__(self, device: xrt.device, kernel: xrt.kernel, instr_v: list[int], instr_bo: xrt.bo):
        self.__device = device
        self.__kernel = kernel
        self.__instr_v = instr_v
        self.__instr_bo = instr_bo
        self.__bos = {}
        self.__next_gid = 3

    def create_inout_bo(self, name: str, volume: int, itemsize: int) -> xrt.bo:
        """Creates an HOST_ONLY buffer object with incremental group_id.

        Parameters
        ----------
        name : str
            The name associated with the buffer object.
        volume : int
            The number of elements in the buffer.
        itemsize : int
            The size of each element in the buffer.

        Returns
        -------
        An xrt buffer object.
        """
        bo = xrt.bo(self.__device, volume * itemsize, xrt.bo.host_only,
                    self.__kernel.group_id(self.__next_gid))
        self.__next_gid += 1
        self.__bos[name] = bo

        return bo

    def get_device(self) -> xrt.device:
        return self.__device

    def get_bo(self, name: str) -> xrt.bo:
        return self.__bos[name]

    def get_kernel(self) -> xrt.kernel:
        return self.__kernel

    def kernel_call(self, *args):
        """Calls the kernel registered on the NPU.

        Parameters
        ----------
        *args : *list[xrt.bo]
            List of buffers to pass to the kernel call.

        Throws
        ------
        Exception
            If the kernel call does not end successfully
        """
        h = self.__kernel(3, self.__instr_bo, len(self.__instr_v), *args)
        r = h.wait()
        if r != xrt.ert_cmd_state.ERT_CMD_STATE_COMPLETED:
            raise Exception(f"Kernel returned {r}")
