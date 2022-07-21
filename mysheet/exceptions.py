from typing import Any, TypeVar


class CyclicDependency(Exception):
    pass


class NotEvaluated(Exception):
    pass


class UnterminatingSlice(Exception):
    def __init__(self, start: int, stop: int, step: int) -> None:
        super().__init__(f"start: {start}, stop: {stop}, step: {step}")


class InvalidFormat(Exception):
    def __init__(self, cls: type, s: str) -> None:
        super().__init__(f"{cls.__name__}: {s}")


class InvalidData(Exception):
    pass


class AccessEmptyCell(Exception):
    def __init__(self, row: str, col: Any) -> None:
        super().__init__(f"row: {row}, col: {col}")
