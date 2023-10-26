import pytest

from resultpipes.catch import *


def test_log_exception():
    log_exc_called = False

    def log_exc(exc: Exception):
        nonlocal log_exc_called
        log_exc_called = True

    exc = Exception()
    assert log_exception(exc, log_exc=log_exc) == exc
    assert log_exc_called


class Error:
    pass


def test_catch():
    def handle_exc(exc: Exception) -> Error:
        return Error()

    @catch(handle_exc)
    def f(x: int) -> Result[int, str]:
        raise TypeError()

    result = f(1)
    match result:
        case Failure(error):
            match error:
                case Error():
                    pass
                case _:
                    assert False
        case _:
            assert False


@pytest.mark.asyncio
async def test_acatch():
    def handle_exc(exc: Exception) -> Error:
        return Error()

    @acatch(handle_exc)
    async def f(x: int) -> Result[int, str]:
        raise TypeError()

    result = await f(1)
    match result:
        case Failure(error):
            match error:
                case Error():
                    pass
                case _:
                    assert False
        case _:
            assert False
