from collections import deque
from io import FileIO
from typing import Deque, Generator, Generic, Mapping, Sequence, Set, Tuple, TypeVar, Union, overload

from .exceptions import NotEvaluated
from .task import Task
from .value_task import Cell, CellValue, Constant, ValueArray, ValueTask
from .ticks import Date, Week, Month
from . import dependency_graph


Tick = TypeVar("Tick", Date, Week, Month)


class Sheet(Generic[Tick]):
    def __init__(self,
                 start: Tick, end: Tick,
                 row_names: Sequence[str]) -> None:
        self.start: Tick = start
        self.end: Tick = end
        self.tick_class = start.__class__
        self.ncol = end - start + 1
        self.row_names = row_names
        self.nrow = len(row_names)
        self.cells = [
            [Cell(row_names[r],
                  str(start + c)) for c in range(self.ncol)]
            for r in range(self.nrow)
        ]
        self.col_index: Mapping[Tick, int] = {
            start + i: i for i in range(self.ncol)
        }
        self.row_index = {
            self.row_names[i]: i for i in range(self.nrow)
        }

    @overload
    def __getitem__(self, pair: Tuple[str, Tick]) -> CellValue:
        ...

    @overload
    def __getitem__(self, pair: Tuple[str, Sequence[Tick]]) -> ValueArray[float]:
        ...

    def __getitem__(self, pair):
        row = self.row_index[pair[0]]
        p1 = pair[1]
        if isinstance(p1, list):
            return ValueArray([
                self.cells[row][c].value
                for c in [
                    self.col_index[x]
                    for x in p1
                ]
            ])
        else:
            col = self.col_index[p1]
            return self.cells[row][col].value

    def __setitem__(self, pair: Tuple[str, Tick], v: Union[ValueTask[float], float, int]):
        if not isinstance(v, ValueTask):
            v2 = Constant(v)
        else:
            v2 = v
        r = self.row_index[pair[0]]
        c = self.col_index[pair[1]]
        self.cells[r][c].formula = v2

    @property
    def columns(self) -> Sequence[Tick]:
        return [self.start + i for i in range(self.ncol)]

    @property
    def col_names(self) -> Sequence[str]:
        return [str(c) for c in self.columns]

    def calculate(self) -> None:
        dependency_graph.get().calculate()

    def get_values(self) -> Sequence[Sequence[float]]:
        return [
            [self[r, c].value for c in self.columns]
            for r in self.row_names
        ]

    def get_parent_cells(self, row: str, _column: Union[str, Tick]) -> Generator[Cell, None, None]:
        if isinstance(_column, str):
            column = self.tick_class.from_str(_column)
        else:
            column = _column
        node = self[row, column]
        g = dependency_graph.get()
        visited: Set[Task] = set()
        stack: Deque[Task] = deque()
        stack.append(node)
        while len(stack) > 0:
            current = stack.pop()
            parents = g.get_parents(current)
            for p in parents:
                if p in visited:
                    continue
                visited.add(p)
                if isinstance(p, CellValue):
                    yield p.cell
                else:
                    stack.append(p)

    def get_child_cells(self, row: str, _column: Union[str, Tick]) -> Generator[Cell, None, None]:
        if isinstance(_column, str):
            column = self.tick_class.from_str(_column)
        else:
            column = _column
        node = self[row, column]
        g = dependency_graph.get()
        visited: Set[Task] = set()
        stack: Deque[Task] = deque()
        stack.append(node)
        while len(stack) > 0:
            current = stack.pop()
            children = g.get_children(current)
            for c in children:
                if c in visited:
                    continue
                visited.add(c)
                if isinstance(c, CellValue):
                    yield c.cell
                else:
                    stack.append(c)

    def update(self, row: str, _column: Union[str, Tick], value: float) -> Sequence[Cell]:
        if isinstance(_column, str):
            column = self.tick_class.from_str(_column)
        else:
            column = _column
        cellVal: CellValue = self[row, column]   # type: ignore
        cell = cellVal.cell
        cell.formula = Constant(value)
        g = dependency_graph.get()
        ret = g.update(cell.formula)
        return [c.cell for c in ret if isinstance(c, CellValue)]

    def to_csv(self, fp):
        def filter(cell: Cell) -> str:
            try:
                v = cell.result
            except NotEvaluated:
                return ""
            if v is None:
                return ""
            return str(v)

        fp.write("\t".join([""] + [str(d) for d in self.columns]) + "\n")
        for i, rn in enumerate(self.row_names):
            fp.write(rn + "\t")
            fp.write("\t".join([filter(v) for v in self.cells[i]]))
            fp.write("\n")

    def get_row(self, row: str) -> Sequence[Cell]:
        idx = self.row_index[row]
        return self.cells[idx]
