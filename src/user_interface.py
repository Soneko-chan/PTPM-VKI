from abc import ABC, abstractmethod


class UserInterface(ABC):

    @abstractmethod
    def get_input(self, prompt: str) -> str:
        pass


class ConsoleUserInterface(UserInterface):

    def get_input(self, prompt: str) -> str:
        return input(prompt)