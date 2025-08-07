import nengo
import nengo.builder

import logging
logger = logging.getLogger(__name__)


class AIEBuilder(nengo.builder.Builder):
    """Clone of the default nengo builder.

    It has been decided to clone the default builder so that registering new builder methods does not affect the default nengo builder.
    Refer to nengo documentation for information about methods, attributes and parameters.
    """
    builders = {}

    def __init__(self):
        super().__init__()
        logger.info("Initialied builder")

    @classmethod
    def build(cls, model, obj, *args, **kwargs):
        try:
            build_result = nengo.builder.Builder.build.__func__(
                AIEBuilder, model, obj, *args, **kwargs)
            logger.debug(f"Using AIE builder for {obj.__class__.__name__}")
            return build_result
        except nengo.exceptions.BuildError:
            logger.debug(f"Using default builder for {obj.__class__.__name__}")
            return nengo.builder.Builder.build.__func__(nengo.builder.Builder, model, obj, *args, **kwargs)
