from mysheet.value_task import Constant, ValueTask, task
from mysheet import dependency_graph
from mysheet.exceptions import CyclicDependency


def test_parent(clear_graph):
    one = Constant(1)
    two = Constant(2)

    @task
    def add(x, y):
        return x + y

    three = add(one, two)
    g = dependency_graph.get()
    ps = g.get_parents(three)
    assert len(list(ps)) == 2


def test_generator(clear_graph):
    one = Constant(1)

    @task
    def add1(x):
        return x + 1

    two = add1(one)
    g = dependency_graph.get()
    gen = g.get_calculation_tasks()
    assert next(gen) == one
    assert next(gen) == two
    try:
        next(gen)
    except StopIteration:
        return
    assert False


def test_evaluate(clear_graph):
    a = Constant(1)
    b = Constant(1)

    @task
    def plus(x, y):
        return x + y

    c = plus(a, b)
    g = dependency_graph.get()
    for t in g.get_calculation_tasks():
        t.run()

    assert c.value == 2


def test_cycle(clear_graph):
    a = Constant(1)
    b = Constant(1)
    c = Constant(1)
    g = dependency_graph.get()
    g.add_dependency(a, b)
    g.add_dependency(b, c)
    g.add_dependency(c, a)

    try:
        next(g.get_calculation_tasks())
        assert False
    except CyclicDependency:
        return


def test_update(clear_graph):
    a = ValueTask(lambda: 1)
    b = ValueTask(lambda: 2)
    c = a + b

    g = dependency_graph.get()
    for t in g.get_calculation_tasks():
        t.run()

    assert c.value == 3

    a.calculate = lambda: 3
    ret = g.update(a)

    assert len(ret) == 2
    assert set(ret) == set([a, c])
    assert c.value == 5
