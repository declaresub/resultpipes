from functools import partial
from typing import Any

import pytest

from resultpipes.pipe import *


class Error:
    pass


class Error1:
    pass


@pipeable
def f(x: str) -> Result[int, Error]:
    try:
        return Success(int(x))
    except ValueError:
        return Failure(Error())


@pipeable
async def f1(x: str) -> Result[int, Error]:
    try:
        return Success(int(x))
    except ValueError:
        return Failure(Error())


@pipeable
def g(x: int) -> Result[int, Error]:
    return Success(x)


@pipeable
async def g1(x: int) -> Result[int, Error]:
    return Success(x)


@pipeable
def h(error: Error) -> Result[int, Error1]:
    return Failure(Error1())


@pipeable
async def h1(error: Error) -> Result[int, Error1]:
    return Failure(Error1())


@pipeable
def id0(r: Result[int, Error]) -> Result[int, Error]:
    return r


@pipeable
async def id1(r: Result[int, Error]) -> Result[int, Error]:
    return r


@pytest.mark.parametrize(
    "f, expected", [(f, False), (f1, True), (partial(f, 1), False)]
)
def test_is_async_callable(f: Any, expected: bool):
    assert is_async_callable(f) == expected


def test_pipeable_call():
    match f("1"):
        case Success(value):
            assert value == 1
        case _:
            assert False


def test_pipe_or_success():
    match (f | g)("1"):
        case Success(value):
            assert value == 1
        case _:
            assert False


def test_pipe_or_failure():
    match (f | g)("x"):
        case Failure(value):
            assert isinstance(value, Error)
        case _:
            assert False


@pytest.mark.parametrize(
    "f, g",
    [
        (f, g1),
        (f1, g),
        (f1, g1),
    ],
)
@pytest.mark.asyncio
async def test_pipe_or_async_success(
    f: Pipeable[str, int, Error] | APipeable[str, int, Error],
    g: APipeable[int, int, Error],
):
    match await (f | g)("1"):
        case Success(value):
            assert value == 1
        case _:
            assert False


@pytest.mark.parametrize("p, q", [(f, g1), (f1, g), (f1, g1)])
@pytest.mark.asyncio
async def test_pipe_or_async_failure(
    p: Pipeable[str, int, Error] | APipeable[str, int, Error],
    q: APipeable[int, int, Error],
):
    match await (p | q)("x"):
        case Failure(value):
            assert isinstance(value, Error)
        case _:
            assert False


def test_pipe_and_success():
    p = f & h
    match p("1"):
        case Success(value):
            assert value == 1
        case _:
            assert False


@pytest.mark.asyncio
async def test_pipe_and_failure():
    p = f & h
    match p("z"):
        case Failure(error):
            assert isinstance(error, Error1)
        case _:
            assert False


@pytest.mark.parametrize(
    "f, h",
    [
        (f, h1),
        (f1, h),
        (f1, h1),
    ],
)
@pytest.mark.asyncio
async def test_pipe_and_async_success(
    f: Pipeable[str, int, Error] | APipeable[str, int, Error],
    h: APipeable[Error, int, Error1],
):
    p = f & h
    match await p("1"):
        case Success(value):
            assert value == 1
        case _:
            assert False


@pytest.mark.parametrize(
    "f, h",
    [
        (f, h1),
        (f1, h),
        (f1, h1),
    ],
)
@pytest.mark.asyncio
async def test_pipe_and_async_failure(
    f: Pipeable[str, int, Error] | APipeable[str, int, Error],
    h: APipeable[Error, int, Error1],
):
    p = f & h
    match await p("z"):
        case Failure(error):
            assert isinstance(error, Error1)
        case _:
            assert False


@pytest.mark.parametrize("x", [Success(1), Failure(Error())])
def test_pipe_xor(x: Result[int, Error]):
    p = id0 ^ id0
    assert p(x) == x


@pytest.mark.parametrize(
    "t1, t2, x",
    [
        (id0, id1, Success(1)),
        (id1, id0, Failure(Error())),
        (id1, id1, Success(1)),
    ],
)
@pytest.mark.asyncio
async def test_pipe_xor_async(
    t1: Pipeable[Result[int, Error], int, Error]
    | APipeable[Result[int, Error], int, Error],
    t2: APipeable[Result[int, Error], int, Error],
    x: Result[int, Error],
):
    p = t1 ^ t2
    assert await p(x) == x
