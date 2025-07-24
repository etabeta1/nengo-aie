import pyxrt as xrt

import logging
logger = logging.getLogger(__name__)


class AIEManager:
    
    @staticmethod
    def init_aie(xclbin_path):
        device = xrt.device(0)
        xclbin = xrt.xclbin(xclbin_path)
        xkernel = xclbin.get_kernels()[0]
        device.register_xclbin(xclbin)
        context = xrt.hw_context(device, xclbin.get_uuid())
        kernel = xrt.kernel(context, xkernel.get_name())
        
        return (device, kernel)