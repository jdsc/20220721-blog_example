from io import IOBase
import json
from typing import Any, Dict, Generic, Sequence, TypeVar, Union
from mysheet.exceptions import InvalidData

from mysheet.ticks import Date, Month, Week


T = TypeVar("T", Date, Week, Month)


class InputData(Generic[T]):
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def first_value_of_starting_inventoy(self) -> float:
        return self.data["期初在庫/実績"]

    @property
    def shipment(self) -> Sequence[float]:
        return self.data["出荷量/実績"]

    @property
    def arrival(self) -> Sequence[float]:
        return self.data["入荷量/実績"]

    def validate(self,
                 learn_start: T, sim_end: T) -> None:
        n = sim_end - learn_start + 1
        if len(self.shipment) != n:
            raise InvalidData(
                f"Length of '出荷量/実績' is invalid. expected: {n}, actual: {len(self.shipment)}")
        if len(self.arrival) != n:
            raise InvalidData(
                f"Length of '入荷量/実績' is invalid. expected: {n}, actual: {len(self.arrival)}")
