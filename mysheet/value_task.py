from __future__ import annotations

from typing import Callable, Generator, Generic, Optional, Sequence, TypeVar, Union


from .exceptions import AccessEmptyCell, NotEvaluated
from .task import Task
from . import dependency_graph

V = TypeVar("V")


def task(f: Callable[..., V]) -> Callable[..., ValueTask[V]]:
    count_of_this_task = 0

    def make_value(*args, **kwargs):
        args2 = [
            v if isinstance(v, ValueTask) else Constant(v)
            for v in args
        ]
        kwargs2 = {
            s: v if isinstance(v, ValueTask) else Constant(v)
            for s, v in kwargs.items()
        }

        def executor():
            args = [v.value for v in args2]
            kwargs = {
                s: v.value
                for s, v in kwargs2.items()
            }
            return f(*args, **kwargs)

        value = ValueTask(executor)
        g = dependency_graph.get()
        for v in args2:
            g.add_dependency(v, value)
        for _, v in kwargs2.items():
            g.add_dependency(v, value)

        nonlocal count_of_this_task
        value.name += f"\n({f.__name__}-{count_of_this_task})"
        count_of_this_task += 1

        return value
    return make_value


class ValueTask(Task, Generic[V]):
    def __init__(self, f: Callable[[], V]) -> None:
        super().__init__()
        self._value: Optional[V] = None
        self.calculate = f

    def execute(self) -> None:
        self._value = self.calculate()

    def __str__(self) -> str:
        return str(self._value)

    @property
    def value(self) -> V:
        if not self.done:
            raise NotEvaluated()
        return self._value  # type: ignore

    def reset(self) -> None:
        super().reset()
        self._value = None

    @task
    def __add__(self, v: Union[V, ValueTask[V]]):
        return self + v

    @task
    def __sub__(self, v: Union[V, ValueTask[V]]):
        return self - v

    @task
    def __mul__(self, v: Union[V, ValueTask[V]]):
        return self * v

    @task
    def __truediv__(self, v: Union[V, ValueTask[V]]):
        return self / v


class Constant(ValueTask[V]):
    def __init__(self, v: V) -> None:
        super().__init__(lambda: v)
        self.run()

    def reset(self) -> None:
        super().reset()
        self.run()


class ValueArray(ValueTask[Sequence[V]]):
    def __init__(self, vs: Sequence[ValueTask[V]]) -> None:
        g = dependency_graph.get()
        for v in vs:
            g.add_dependency(v, self)

        def calculate():
            return [v.value for v in vs]

        super().__init__(calculate)
        self.vs = vs

        def __iter__(self) -> Generator[ValueTask[V], None, None]:
            return self.vs


class Cell:
    def __init__(self, row: str, col: str):
        self.value = CellValue(self)
        self._formula: Optional[ValueTask[float]] = None
        self.row = row
        self.col = col

    @property
    def name(self) -> str:
        return f"({self.row}, {self.col})"

    @property
    def formula(self) -> ValueTask[float]:
        if self._formula is None:
            raise AccessEmptyCell(self.row, self.col)
        return self._formula

    @formula.setter
    def formula(self, v: Union[float, ValueTask[float]]) -> None:
        new_v = v if isinstance(v, ValueTask) else Constant(v)
        g = dependency_graph.get()
        try:
            old_v = self.formula
            g.remove_dependency(old_v, self.value)
        except AccessEmptyCell:
            pass
        g.add_dependency(new_v, self.value)

        self._formula = new_v

    @property
    def result(self) -> float:
        return self.value.value

    @property
    def empty(self) -> bool:
        return self._formula is None


class CellValue(ValueTask[float]):
    def __init__(self, cell: Cell) -> None:
        self.cell = cell
        super().__init__(lambda: self.cell.formula.value)
