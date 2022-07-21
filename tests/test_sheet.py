from typing import Sequence
from mysheet.exceptions import AccessEmptyCell, CyclicDependency
from mysheet.sheet import Sheet
from mysheet.ticks import Date
from mysheet.value_task import task


def test_calc(clear_graph):
    ncol = 10
    start = Date(2021, 1, 1)
    end = start + ncol - 1
    a, b = "a", "b"
    sheet = Sheet(start, end, [a, b])
    sheet[a, Date(2021, 1, 1)] = 1
    sheet[b, Date(2021, 1, 1)] = 1
    for i in range(1, ncol):
        sheet[a, start + i] = sheet[a, start + i - 1] + 1
    for i in range(1, ncol):
        sheet[b, start + i] = \
            sheet[b, start + i - 1] + sheet[a, start + i]

    sheet.calculate()
    cellValue = sheet[b, end]
    assert cellValue.value is not None and cellValue.value == 55


def test_order(clear_graph):
    ncol = 10
    start = Date(2021, 1, 1)
    end = start + ncol - 1
    a, b = "a", "b"
    sheet = Sheet(start, end, [a, b])
    current = end
    while current > start:
        sheet[a, current] = sheet[a, current - 1] + 1
        sheet[b, current] = (
            sheet[b, current - 1] +
            sheet[a, current])
        current -= 1
    sheet[a, start] = 1
    sheet[b, start] = 1

    sheet.calculate()
    cellValue = sheet[b, end]
    assert cellValue.value is not None and cellValue.value == 55


def test_cycle(clear_graph):
    ncol = 10
    start = Date(2021, 1, 1)
    end = start + ncol - 1
    a, b = "a", "b"
    sheet = Sheet(start, end, [a, b])
    sheet[a, start] = sheet[a, start + 1]
    sheet[b, start] = sheet[a, start]
    sheet[b, start + 1] = sheet[b, start]
    sheet[a, start + 1] = sheet[b, start + 1]
    try:
        sheet.calculate()
        assert False
    except CyclicDependency:
        pass


def test_update(clear_graph):
    ncol = 10
    start = Date(2021, 1, 1)
    end = start + ncol - 1
    a, b = "a", "b"
    sheet = Sheet(start, end, [a, b])

    for i in range(ncol):
        sheet[a, start + i] = i
        sheet[b, start + i] = i + 100

    sheet[a, start] = \
        sheet[a, start + 1] + sheet[b, start + 1]
    sheet[a, start] = \
        sheet[a, start + 2] + sheet[b, start + 2]

    sheet.calculate()
    assert sheet[a, start].value == 104


def test_update2(clear_graph):
    start = Date(2000, 1, 1)
    end = Date(2000, 1, 2)
    cols = ["a", "b", "c"]

    sheet = Sheet(start, end, cols)
    sheet["a", start] = 1
    sheet["a", end] = 2
    sheet["b", start] = \
        sheet["a", start] + sheet["a", end]
    sheet["c", start] = \
        sheet["b", start] + 1
    sheet.calculate()

    ret = sheet.update("a", start, 100.0)
    assert len(ret) == 3
    assert set(ret) == set([
        sheet["a", start].cell,
        sheet["b", start].cell,
        sheet["c", start].cell
    ])


def test_slice(clear_graph):
    ncol = 10
    start = Date(2021, 1, 1)
    end = start + ncol - 1
    a, b = "a", "b"
    sheet = Sheet(start, end, [a, b])

    for i in range(ncol):
        sheet[a, start + i] = i

    @task
    def sum(args: Sequence[float]) -> float:
        ret = 0
        for a in args:
            ret += a
        return ret

    for i in range(ncol):
        cells = sheet[a, start[0:(i+1)]]
        sheet[b, start + i] = sum(cells)
    sheet.calculate()

    s = 0
    for i in range(ncol):
        s += i
        assert sheet[b, start + i].value == s


def test_empty(clear_graph):
    start = Date(2000, 1, 1)
    end = Date(2000, 1, 2)
    sheet = Sheet(start, end, ["a"])
    sheet["a", start] = sheet["a", end]
    try:
        sheet.calculate()
        assert False
    except AccessEmptyCell:
        pass


def test_parent_cells(clear_graph):
    start = Date(2000, 1, 1)
    end = Date(2000, 1, 3)
    cols = ["a", "b", "c"]
    sheet = Sheet(start, end, cols)

    @task
    def sum(args: Sequence[float]) -> float:
        ret = 0
        for a in args:
            ret += a
        return ret

    sheet["a", start] = 1
    sheet["a", start + 1] = 1
    sheet["a", start + 2] = 1

    sheet["b", start] = sum(sheet["a", start[0:3]])

    sheet["c", start] = \
        sheet["a", start] + \
        sheet["b", start]

    ps1 = set(sheet.get_parent_cells("b", start))
    assert ps1 == set([sheet["a", start].cell,
                       sheet["a", start + 1].cell,
                       sheet["a", start + 2].cell])
    ps2 = set(sheet.get_parent_cells("c", start))
    assert ps2 == set([sheet["a", start].cell,
                       sheet["b", start].cell])


def test_child_cells(clear_graph):
    start = Date(2000, 1, 1)
    end = Date(2000, 1, 3)
    cols = ["a", "b", "c"]
    sheet = Sheet(start, end, cols)

    @task
    def sum(args: Sequence[float]) -> float:
        ret = 0
        for a in args:
            ret += a
        return ret

    sheet["a", start] = 1
    sheet["a", start + 1] = 1
    sheet["a", start + 2] = 1

    sheet["b", start] = sum(sheet["a", start[0:3]])

    sheet["c", start] = \
        sheet["a", start] + \
        sheet["b", start]

    ps1 = set(sheet.get_child_cells("a", start))
    assert ps1 == set([sheet["b", start].cell, sheet["c", start].cell])

    ps2 = set(sheet.get_child_cells("a", start + 1))
    ps3 = set(sheet.get_child_cells("a", start + 2))
    assert ps2 == ps3 == set([sheet["b", start].cell])

    ps4 = set(sheet.get_child_cells("b", start))
    assert ps4 == set([sheet["c", start].cell])
