from __future__ import annotations

from types import NotImplementedType
from typing import Any, Generic, TypeAlias, TypeVar, overload

R = TypeVar("R", covariant=True)
T = TypeVar("T", covariant=True)
S = TypeVar("S", covariant=True)
E = TypeVar("E", covariant=True)
E1 = TypeVar("E1", covariant=True)


class _Result(Generic[R]):
    _value: R
    __match_args__ = ("value",)
    __slots__ = ("_value",)

    @overload
    def __init__(self, value: _Result[R]) -> None:
        ...  # pragma: no cover

    @overload
    def __init__(self, value: R) -> None:
        ...  # pragma: no cover

    def __init__(self, value: Any = True):
        self._value = value.value if isinstance(value, self.__class__) else value
            

    def __eq__(self, __value: object) -> bool | NotImplementedType:
        return (
            self._value == __value._value
            if isinstance(__value, self.__class__)
            else NotImplemented
        )

    def __hash__(self):
        return hash(self._value)

    @property
    def value(self) -> R:
        return self._value


class Success(_Result[S]):
    pass


class Failure(_Result[E]):
    pass


Result: TypeAlias = Success[S] | Failure[E]
