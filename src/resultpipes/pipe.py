from __future__ import annotations

import asyncio
from functools import partial, wraps
from typing import (
    Any,
    Callable,
    Coroutine,
    Generic,
    Never,
    ParamSpec,
    TypeAlias,
    TypeGuard,
    TypeVar,
    overload,
)

from typing_extensions import assert_never  # added to typinhg in python 3.11.

from .result import Failure, Result, Success


def is_async_callable(obj: Any) -> TypeGuard[Any]:
    # borrowed from starlette
    while isinstance(obj, partial):
        obj = obj.func

    return asyncio.iscoroutinefunction(obj) or (
        callable(obj) and asyncio.iscoroutinefunction(obj.__call__)
    )


def is_not_async_callable(obj: Any) -> TypeGuard[Any]:
    return not is_async_callable(obj)


X = TypeVar("X")
Y = TypeVar("Y")
Z = TypeVar("Z")
E = TypeVar("E")
E1 = TypeVar("E1")
Y1 = TypeVar("Y1")
P = ParamSpec("P")
R = TypeVar("R")


P_s: TypeAlias = Callable[[X], Result[Y, E]]
# type P_s[X, Y, E] = Callable[[X], Result[Y, E]]


class Pipeable(Generic[X, Y, E]):
    def __init__(self, func: P_s[X, Y, E]):
        self.func = func

    def __call__(self, x: X) -> Result[Y, E]:
        return self.func(x)

    @overload
    def pipe_success(self, rhs: Pipeable[Y, Z, E1]) -> Pipeable[X, Z, E | E1]:
        ...  # pragma: no cover

    @overload
    def pipe_success(self, rhs: APipeable[Y, Z, E1]) -> APipeable[X, Z, E | E1]:
        ...  # pragma: no cover

    def pipe_success(
        self, rhs: Pipeable[Y, Z, E1] | APipeable[Y, Z, E1]
    ) -> Pipeable[X, Z, E | E1] | APipeable[X, Z, E | E1]:
        match rhs:
            case APipeable():

                async def ainvoke(x: X) -> Result[Z, E | E1]:
                    result = self(x)
                    match result:
                        case Success():
                            return await rhs(result.value)
                        case Failure():
                            return result

                return APipeable(ainvoke)
            case Pipeable():

                def invoke(x: X) -> Result[Z, E | E1]:
                    result = self(x)
                    match result:
                        case Success():
                            return rhs(result.value)
                        case Failure():
                            return result

                return Pipeable(invoke)
            case _ as oops:  # pragma: no cover # type: ignore
                assert_never(oops)

    __or__ = pipe_success

    @overload
    def pipe_failure(self, rhs: Pipeable[E, Y1, E1]) -> Pipeable[X, Y | Y1, E1]:
        ...  # pragma: no cover

    @overload
    def pipe_failure(self, rhs: APipeable[E, Y1, E1]) -> APipeable[X, Y | Y1, E1]:
        ...  # pragma: no cover

    def pipe_failure(
        self, rhs: Pipeable[E, Y1, E1] | APipeable[E, Y1, E1]
    ) -> Pipeable[X, Y | Y1, E1] | APipeable[X, Y | Y1, E1]:
        match rhs:
            case APipeable():

                async def ainvoke(x: X) -> Result[Y | Y1, E1]:
                    result = self(x)
                    match result:
                        case Success():
                            return result
                        case Failure():
                            return await rhs(result.value)

                return APipeable(ainvoke)
            case Pipeable():

                def invoke(x: X) -> Result[Y | Y1, E1]:
                    result = self(x)
                    match result:
                        case Success():
                            return result
                        case Failure():
                            return rhs(result.value)

                return Pipeable(invoke)
            case _ as oops:  # pragma: no cover # type: ignore
                assert_never(oops)

    __and__ = pipe_failure

    @overload
    def pipe_result(self, rhs: Pipeable[Result[Y, E], Z, E1]) -> Pipeable[X, Z, E | E1]:
        ...  # pragma: no cover

    @overload
    def pipe_result(
        self, rhs: APipeable[Result[Y, E], Z, E1]
    ) -> APipeable[X, Z, E | E1]:
        ...  # pragma: no cover

    def pipe_result(
        self, rhs: Pipeable[Result[Y, E], Z, E1] | APipeable[Result[Y, E], Z, E1]
    ) -> Pipeable[X, Z, E | E1] | APipeable[X, Z, E | E1]:
        match rhs:
            case APipeable():

                async def ainvoke(x: X) -> Result[Z, E | E1]:
                    return await rhs(self(x))

                return APipeable(ainvoke)
            case Pipeable():

                def invoke(x: X) -> Result[Z, E | E1]:
                    return rhs(self(x))

                return Pipeable(invoke)
            case _ as oops:  # pragma: no cover # type: ignore
                assert_never(oops)

    __xor__ = pipe_result


P_a: TypeAlias = Callable[[X], Coroutine[Any, Any, Result[Y, E]]]
# type P_a[X, Y, E] = Callable[[X], Coroutine[Any, Any, Result[Y, E]]]


class APipeable(Generic[X, Y, E]):
    def __init__(self, func: P_a[X, Y, E]):
        self.func = func

    async def __call__(self, x: X) -> Result[Y, E]:
        return await self.func(x)

    @overload
    def __or__(self, rhs: Pipeable[Y, Z, E1]) -> APipeable[X, Z, E | E1]:
        ...  # pragma: no cover

    @overload
    def __or__(self, rhs: APipeable[Y, Z, E1]) -> APipeable[X, Z, E | E1]:
        ...  # pragma: no cover

    def __or__(
        self, rhs: Pipeable[Y, Z, E1] | APipeable[Y, Z, E1]
    ) -> APipeable[X, Z, E | E1]:
        async def ainvoke(x: X) -> Result[Z, E | E1]:
            result = await self(x)
            match result:
                case Success(value):
                    match rhs:
                        case APipeable():
                            return await rhs(value)
                        case Pipeable():
                            return rhs(value)
                case Failure():
                    return result
                case _ as oops:  # pragma: no cover # type: ignore
                    assert_never(oops)

        return APipeable(ainvoke)

    @overload
    def pipe_failure(self, rhs: Pipeable[E, Y1, E1]) -> APipeable[X, Y | Y1, E1]:
        ...  # pragma: no cover

    @overload
    def pipe_failure(self, rhs: APipeable[E, Y1, E1]) -> APipeable[X, Y | Y1, E1]:
        ...  # pragma: no cover

    def pipe_failure(
        self, rhs: Pipeable[E, Y1, E1] | APipeable[E, Y1, E1]
    ) -> APipeable[X, Y | Y1, E1]:
        async def ainvoke(x: X) -> Result[Y, E1]:
            result = await self(x)
            match result:
                case Success():
                    return result
                case Failure(error):
                    if is_async_callable(rhs):
                        return await rhs(error)
                    else:
                        assert is_not_async_callable(rhs)
                        return rhs(error)
                case _ as oops:  # pragma: no cover # type: ignore
                    assert_never(oops)

        return APipeable(ainvoke)

    __and__ = pipe_failure

    @overload
    def pipe_result(self, rhs: Pipeable[Result[Y, E], Z, E1]) -> APipeable[X, Z, E1]:
        ...  # pragma: no cover

    @overload
    def pipe_result(self, rhs: APipeable[Result[Y, E], Z, E1]) -> APipeable[X, Z, E1]:
        ...  # pragma: no cover

    def pipe_result(
        self, rhs: Pipeable[Result[Y, E], Z, E1] | APipeable[Result[Y, E], Z, E1]
    ) -> APipeable[X, Z, E1]:
        match rhs:
            case APipeable():

                async def ainvoke(x: X) -> Result[Z, E1]:
                    return await rhs(await self(x))

                return APipeable(ainvoke)
            case Pipeable():

                async def invoke(x: X) -> Result[Z, E1]:
                    return rhs(await self(x))

                return APipeable(invoke)
            case _ as oops:  # pragma: no cover # type: ignore
                assert_never(oops)

    __xor__ = pipe_result


@overload
def pipeable(f: P_s[X, Y, E]) -> Pipeable[X, Y, E]:
    ...  # pragma: no cover


@overload
def pipeable(f: P_a[X, Y, E]) -> APipeable[X, Y, E]:
    ...  # pragma: no cover


def pipeable(f: P_s[X, Y, E] | P_a[X, Y, E]) -> Pipeable[X, Y, E] | APipeable[X, Y, E]:
    if is_async_callable(f):
        return APipeable(f)
    else:
        assert is_not_async_callable(f)
        return Pipeable(f)


@overload
def success(  # pyright: ignore [reportOverlappingOverload]
    f: Callable[P, Coroutine[Any, Any, R]]
) -> Callable[P, Coroutine[Any, Any, Result[R, Never]]]:
    ...  # pragma: no cover


@overload
def success(f: Callable[P, R]) -> Callable[P, Result[R, Never]]:
    ...  # pragma: no cover


def success(
    f: Callable[P, R] | Callable[P, Coroutine[Any, Any, R]]
) -> Callable[P, Result[R, Never]] | Callable[P, Coroutine[Any, Any, Result[R, Never]]]:
    """decorator that transforms a function f with return type T to a function that returns Result[T, Never]."""
    if is_async_callable(f):

        async def _a(*args: P.args, **kwargs: P.kwargs) -> Result[R, Never]:
            x = await f(*args, **kwargs)
            return Success(x)

        return _a
    else:
        assert is_not_async_callable(f)

        # f = cast(Callable[P, R], f)
        @wraps(f)
        def _f(*args: P.args, **kwargs: P.kwargs) -> Result[R, Never]:
            x = f(*args, **kwargs)
            return Success(x)

        return _f


@overload
def failure(  # pyright: ignore [reportOverlappingOverload]
    f: Callable[P, Coroutine[Any, Any, R]]
) -> Callable[P, Coroutine[Any, Any, Result[Never, R]]]:
    ...  # pragma: no cover


@overload
def failure(f: Callable[P, R]) -> Callable[P, Result[Never, R]]:
    ...  # pragma: no cover


def failure(
    f: Callable[P, R] | Callable[P, Coroutine[Any, Any, R]]
) -> Callable[P, Result[Never, R]] | Callable[P, Coroutine[Any, Any, Result[Never, R]]]:
    """decorator that transforms a function f with return type T to a function that returns Result[T, Never]."""
    if is_async_callable(f):

        async def _a(*args: P.args, **kwargs: P.kwargs) -> Result[Never, R]:
            x = await f(*args, **kwargs)
            return Failure(x)

        return _a
    else:
        assert is_not_async_callable(f)

        # f = cast(Callable[P, R], f)
        @wraps(f)
        def _f(*args: P.args, **kwargs: P.kwargs) -> Result[Never, R]:
            x = f(*args, **kwargs)
            return Failure(x)

        return _f
