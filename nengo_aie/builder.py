import nengo.builder
from nengo.exceptions import BuildError

class AIEBuilder(nengo.builder.Builder):
    builders = {}

    @classmethod
    def build(cls, model, obj, *args, **kwargs):
        try:
            return nengo.builder.Builder.build.__func__(AIEBuilder, model, obj, *args, **kwargs)
        except BuildError:
            return nengo.builder.Builder.build.__func__(nengo.builder.Builder, model, obj, *args, **kwargs)