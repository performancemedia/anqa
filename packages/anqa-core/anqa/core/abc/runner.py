from abc import ABC, abstractmethod


class AbstractRunner(ABC):
    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError
