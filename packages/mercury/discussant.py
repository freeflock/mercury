from abc import abstractmethod, ABC


class Discussant(ABC):
    @abstractmethod
    def generate_prompt(self):
        pass

    @abstractmethod
    def add_message(self, message):
        pass
