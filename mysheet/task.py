from __future__ import annotations
from abc import ABC, abstractmethod


class Task(ABC):
    def __init__(self) -> None:
        self.done: bool = False
        self._name = f"[{id(self)}]"

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, s: str) -> None:
        self._name = s

    def run(self) -> None:
        if self.done:
            return
        self.execute()
        self.done = True

    def reset(self) -> None:
        self.done = False

    @abstractmethod
    def execute(self) -> None:
        pass
