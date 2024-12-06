from abc import abstractmethod, ABC

from ratatosk_errands.model import Echo


class Dialog(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def step(self, echo: Echo):
        pass

    @abstractmethod
    def finished(self):
        pass

    @abstractmethod
    def get_dialog(self):
        pass

    @abstractmethod
    def get_identifier(self):
        pass
