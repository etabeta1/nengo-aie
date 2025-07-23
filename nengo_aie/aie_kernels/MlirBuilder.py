from abc import ABC, abstractmethod


class MlirBuilder(ABC):
    def __init__(self, filename):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    @abstractmethod
    def build(self):
        pass
