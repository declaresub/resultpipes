from __future__ import annotations

from functools import wraps
from logging import getLogger
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar, cast, overload

from .result import Failure, Result

log = getLogger(__name__)

P = ParamSpec("P")
S = TypeVar("S")
E = TypeVar("E")
E1 = TypeVar("E1")


def log_exception(
    exc: Exception, log_exc: Callable[[Exception], None] = log.exception
) -> Exception:
    assert isinstance(exc, Exception)
    log_exc(exc)
    return exc


@overload
def catch() -> (
    Callable[[Callable[P, Result[S, E]]], Callable[P, Result[S, E | Exception]]]
):
    ...  # pragma: no cover


@overload
def catch(
    handle_exc: Callable[[Exception], E1]
) -> Callable[[Callable[P, Result[S, E]]], Callable[P, Result[S, E | E1]]]:
    ...  # pragma: no cover


# Because catch, acatch have the same parameters, we can't overload catch to replace acatch.
# and we have to declare handle_exc as optional and set the default in the function to get both pyright
# and mypy to be happy.
def catch(
    handle_exc: Callable[[Exception], E1] | None = None
) -> Callable[[Callable[P, Result[S, E]]], Callable[P, Result[S, E | E1]]]:
    if handle_exc is None:
        handle_exc = cast(Callable[[Exception], E1], log.exception)  # pragma: no cover

    def decorator(f: Callable[P, Result[S, E]]) -> Callable[P, Result[S, E | E1]]:
        @wraps(f)
        def wrapped(*args: P.args, **kwargs: P.kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as exc:
                return Failure(handle_exc(exc))

        return wrapped

    return decorator


@overload
def acatch() -> (
    Callable[
        [Callable[P, Coroutine[Any, Any, Result[S, E]]]],
        Callable[P, Coroutine[Any, Any, Result[S, E | Exception]]],
    ]
):
    ...  # pragma: no cover


@overload
def acatch(
    handle_exc: Callable[[Exception], E1]
) -> Callable[
    [Callable[P, Coroutine[Any, Any, Result[S, E]]]],
    Callable[P, Coroutine[Any, Any, Result[S, E | E1]]],
]:
    ...  # pragma: no cover


def acatch(
    handle_exc: Callable[[Exception], E1] | None = None
) -> Callable[
    [Callable[P, Coroutine[Any, Any, Result[S, E]]]],
    Callable[P, Coroutine[Any, Any, Result[S, E | E1]]],
]:
    if handle_exc is None:
        handle_exc = cast(Callable[[Exception], E1], log.exception)  # pragma: no cover

    def decorator(
        f: Callable[P, Coroutine[Any, Any, Result[S, E]]]
    ) -> Callable[P, Coroutine[Any, Any, Result[S, E | E1]]]:
        @wraps(f)
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> Result[S, E | E1]:
            try:
                return await f(*args, **kwargs)
            except Exception as exc:
                return Failure(handle_exc(exc))

        return wrapped

    return decorator
