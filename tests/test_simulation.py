#!/usr/bin/env python

import logging
import random


from mysheet.value_task import Constant, task
from mysheet.sheet import Sheet
from mysheet.ticks import Date

LOGGER = logging.getLogger(__name__)


@task
def sales():
    "販売数は、0-10個の間の乱数"
    return float(random.randint(0, 10))


@task
def order_rule(inv_end):
    "期末在庫が3個以下だったら5個発注する"
    if inv_end <= 3:
        return 5.0
    else:
        return 0.0


@task
def calc_inv(inv_start, num_sales, num_arrive):
    n = inv_start - num_sales + num_arrive
    if n >= 0:
        return float(n)
    else:
        return 0.0


def test_simulation(clear_graph):
    start = Date(2022, 1, 1)
    end = Date(2022, 1, 3)
    rows = [
        "start_inv",
        "end_inv",
        "order",
        "sales",
        "arrive"
    ]
    sheet = Sheet(
        start, end, rows
    )

    today = start

    # 初日の設定
    ten = Constant(10)
    sheet["start_inv", today] = ten + ten
    sheet["arrive", today] = 0

    while today <= end:
        sheet["sales", today] = sales()

        if today > start:
            sheet["arrive", today] = sheet["order", today - 1]

        sheet["end_inv", today] = \
            calc_inv(sheet["start_inv", today],
                     sheet["sales", today],
                     sheet["arrive", today])

        sheet["order", today] = order_rule(
            sheet["end_inv", today])

        if today < end:
            sheet["start_inv", today + 1] = sheet["end_inv", today]

        today = today + 1

    # debug
    from mysheet import dependency_graph
    g = dependency_graph.get()
    g.to_dot("/tmp/graph.dot")
    with open("/tmp/list.txt", "w") as f:
        for t in g.get_calculation_tasks():
            f.write(t.name + "\n")

    sheet.calculate()
    print(sheet["start_inv", end].value)
