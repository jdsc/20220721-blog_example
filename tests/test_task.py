from mysheet.exceptions import NotEvaluated
from mysheet.value_task import Constant, ValueArray, ValueTask, task
from mysheet import dependency_graph


def test_constant():
    one = Constant(1)
    assert one.done
    assert one.value == 1

    one.reset()
    assert one.done
    assert one.value == 1


def test_value():
    to_be_one = ValueTask(lambda: 1)
    assert not to_be_one.done
    try:
        to_be_one.value
        assert False
    except NotEvaluated:
        pass
    to_be_one.run()
    assert to_be_one.done
    assert to_be_one.value == 1


def test_calc():
    """
    ValueTask同士の計算を確認する
    """
    five = Constant(5)

    @task
    def plus(x, y):
        return x + y

    ret = plus(five, five)
    assert not ret.done

    ret.run()
    assert ret.done
    assert ret.value == 10


def test_calc2():
    """
    ValueTaskとリテラルの計算を確認する
    """
    five = Constant(5)

    @task
    def plus1(x):
        return x + 1

    ret = plus1(five)
    assert not ret.done

    ret.run()
    assert ret.done
    assert ret.value == 6


def test_plus(clear_graph):
    """
    演算子によるValueTaskの計算を確認する
    """
    one = Constant(1)
    three = one + one + one
    dependency_graph.get().calculate()

    assert three.value == 3


def test_plus2(clear_graph):
    """
    演算子を用いた、リテラルとValueTaskの混ざった計算を確認する
    """
    one = Constant(1)
    three = one + one + 1
    dependency_graph.get().calculate()

    assert three.value == 3


def test_array(clear_graph):
    """
    ValueArrayの動作検証
    """
    one = Constant(1.0)
    two: ValueTask[float] = one + one
    array = ValueArray([one, two])
    dependency_graph.get().calculate()

    assert len(array.value) == 2
    assert array.value[0] == 1
    assert array.value[1] == 2


def test_reset(clear_graph):
    t = ValueTask(lambda: 1)
    t.run()
    assert t.value == 1
    t.reset()
    try:
        t.value
        assert False
    except NotEvaluated:
        pass
