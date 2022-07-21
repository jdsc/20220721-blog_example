from __future__ import annotations

from datetime import date as _date, timedelta
from typing import Generic, List, Pattern, Sequence, TypeVar, Union, overload
from dataclasses import dataclass
import re

from mdweek import Week as MDWeek

from mysheet.exceptions import InvalidFormat, UnterminatingSlice


class SliceMixIn:
    def __getitem__(self, sl: slice) -> Sequence[SliceMixIn]:
        start = sl.start or 0
        stop = sl.stop
        if stop is None:
            raise UnterminatingSlice(sl.start, sl.stop, sl.step)
        step = sl.step or (1 if start < stop else -1)
        if (start < stop and step < 0) or \
           (start > stop and step > 0) or \
           (start != stop and step == 0):
            raise UnterminatingSlice(sl.start, sl.stop, sl.step)

        ret: List[SliceMixIn] = []
        if step > 0:
            while start < stop:
                ret.append(self + start)  # type: ignore
                start += step
        elif step == 0:
            ret.append(start)
        else:
            while start > stop:
                ret.append(self + start)  # type: ignore
                start += step
        return ret


# todo: SliceMixInの型変数に自分を渡す方法が分からん
@dataclass(frozen=True)
class Date(SliceMixIn):
    year: int
    month: int
    day: int

    @property
    def date(self) -> _date:
        return _date(self.year, self.month, self.day)

    @staticmethod
    def from_date(d: _date) -> Date:
        return Date(d.year, d.month, d.day)

    @staticmethod
    def from_str(s: str) -> Date:
        y, m, d = tuple(map(int, s.split("-")))
        return Date(y, m, d)

    def __lt__(self, other: Date) -> bool:
        return self.date < other.date

    def __gt__(self, other: Date) -> bool:
        return self.date > other.date

    def __le__(self, other: Date) -> bool:
        return self.date <= other.date

    def __ge__(self, other: Date) -> bool:
        return self.date >= other.date

    def __add__(self, n: int) -> Date:
        return Date.from_date(self.date + timedelta(days=n))

    @overload
    def __sub__(self, arg: int) -> Date:
        ...

    @overload
    def __sub__(self, arg: Date) -> int:
        ...

    def __sub__(self, arg: Union[int, Date]):
        if isinstance(arg, int):
            return self + (-arg)
        if isinstance(arg, Date):
            return (self.date - arg.date).days

    def __getitem__(self, sl: slice) -> Sequence[Date]:
        return super().__getitem__(sl)  # type: ignore

    def __str__(self) -> str:
        return f"{self.year:04}-{self.month:02}-{self.day:02}"


@dataclass(frozen=True)
class Week(SliceMixIn):
    year: int
    week: int
    pattern = re.compile(r"([0-9]{4})-W([0-9]{2})")

    def to_mdweek(self) -> MDWeek:
        return MDWeek(self.year, self.week)

    @staticmethod
    def from_week(w: MDWeek) -> Week:
        return Week(w.year, w.week)

    @classmethod
    def from_str(cls, s: str) -> Week:
        ret = cls.pattern.match(s)
        if ret is None:
            raise InvalidFormat(cls, s)
        y, w = ret.group(0), ret.group(1)
        return Week(int(y), int(w))

    def __lt__(self, other: Week) -> bool:
        return self.to_mdweek() < other.to_mdweek()

    def __gt__(self, other: Week) -> bool:
        return self.to_mdweek() > other.to_mdweek()

    def __le__(self, other: Week) -> bool:
        return self.to_mdweek() <= other.to_mdweek()

    def __ge__(self, other: Week) -> bool:
        return self.to_mdweek() >= other.to_mdweek()

    def __add__(self, n: int) -> Week:
        return Week.from_week(self.to_mdweek() + n)

    @overload
    def __sub__(self, arg: int) -> Week:
        ...

    @overload
    def __sub__(self, arg: Week) -> int:
        ...

    def __sub__(self, arg: Union[int, Week]):
        if isinstance(arg, int):
            return self + (-arg)
        if isinstance(arg, Week):
            return self.to_mdweek() - arg.to_mdweek()

    def __getitem__(self, sl: slice) -> Sequence[Week]:
        return super().__getitem__(sl)  # type: ignore

    def __str__(self) -> str:
        return f"{self.year:04}-W{self.week:02}"


@dataclass(frozen=True)
class Month(SliceMixIn):
    year: int
    month: int
    pattern = re.compile(r"([0-9]{4})-M([0-9]{2})")

    @classmethod
    def from_str(cls, s: str) -> Month:
        ret = cls.pattern.match(s)
        if ret is None:
            raise InvalidFormat(cls, s)
        y, m = ret.group(0), ret.group(1)
        return Month(int(y), int(m))

    def __lt__(self, other: Month) -> bool:
        if self.year < other.year:
            return True
        elif self.year > other.year:
            return False
        else:
            return self.month < other.month

    def __le__(self, other: Month) -> bool:
        if self.year < other.year:
            return True
        elif self.year > other.year:
            return False
        else:
            return self.month <= other.month

    def __gt__(self, other: Month) -> bool:
        return not self <= other

    def __ge__(self, other: Month) -> bool:
        return not self < other

    def __add__(self, n: int) -> Month:
        y = self.year
        m = self.month + n
        d, r = m // 12, m % 12
        if r == 0:
            r = 12
            d -= 1
        return Month(y + d, r)

    @overload
    def __sub__(self, arg: int) -> Month:
        ...

    @overload
    def __sub__(self, arg: Month) -> int:
        ...

    def __sub__(self, arg: Union[int, Month]):
        if isinstance(arg, int):
            return self + (-arg)
        if isinstance(arg, Month):
            y = self.year - arg.year
            return y * 12 + self.month - arg.month

    def __getitem__(self, sl: slice) -> Sequence[Month]:
        return super().__getitem__(sl)  # type: ignore

    def __str__(self) -> str:
        return f"{self.year:04}-{self.month:02}"
