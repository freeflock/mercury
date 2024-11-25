from abc import abstractmethod, ABC


class Discussant(ABC):
    @abstractmethod
    def generate_instructions(self):
        pass

    @abstractmethod
    def add_message(self, message):
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
