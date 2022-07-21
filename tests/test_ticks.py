from mysheet.ticks import Month, Date, Week


def test_month_add():
    base = Month(2000, 1)
    assert base + (-13) == Month(1998, 12)
    assert base + (-12) == Month(1999, 1)
    assert base + (-11) == Month(1999, 2)
    assert base + (-10) == Month(1999, 3)
    assert base + (-9) == Month(1999, 4)
    assert base + (-8) == Month(1999, 5)
    assert base + (-7) == Month(1999, 6)
    assert base + (-6) == Month(1999, 7)
    assert base + (-5) == Month(1999, 8)
    assert base + (-4) == Month(1999, 9)
    assert base + (-3) == Month(1999, 10)
    assert base + (-2) == Month(1999, 11)
    assert base + (-1) == Month(1999, 12)
    assert base + 0 == Month(2000, 1)
    assert base + 1 == Month(2000, 2)
    assert base + 2 == Month(2000, 3)
    assert base + 3 == Month(2000, 4)
    assert base + 4 == Month(2000, 5)
    assert base + 5 == Month(2000, 6)
    assert base + 6 == Month(2000, 7)
    assert base + 7 == Month(2000, 8)
    assert base + 8 == Month(2000, 9)
    assert base + 9 == Month(2000, 10)
    assert base + 10 == Month(2000, 11)
    assert base + 11 == Month(2000, 12)
    assert base + 12 == Month(2001, 1)
    assert base + 13 == Month(2001, 2)


def test_month_sub():
    base = Month(2000, 1)

    for i in range(-100, 100):
        m = base + i
        assert m - base == i
        assert m - i == base


def test_comp():
    m1 = Month(2000, 1)
    m2 = Month(2000, 2)
    assert m1 <= m2
    assert m1 < m2
    assert not m1 >= m2
    assert not m1 > m2

    d1 = Date(2000, 1, 1)
    d2 = Date(2000, 1, 2)
    assert d1 <= d2
    assert d1 < d2
    assert not d1 >= d2
    assert not d1 > d2

    w1 = Week(2000, 1)
    w2 = Week(2000, 2)
    assert w1 <= w2
    assert w1 < w2
    assert not w1 >= w2
    assert not w1 > w2


def test_slice():
    d = Date(2000, 1, 1)
    l = d[10:20:3]
    assert l[0] == d + 10
    assert l[1] == d + 13
    assert l[2] == d + 16
    assert l[3] == d + 19
    assert len(l) == 4

    l2 = d[-1:-4]
    assert len(l2) == 3
    for i, diff in enumerate(range(-1, -4, -1)):
        assert l2[i] == d + diff
