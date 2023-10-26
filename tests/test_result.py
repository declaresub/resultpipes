from resultpipes.result import Failure, Success


def test_success_init():
    value = 1
    result = Success(value)
    assert result.value == value


def test_success_init_success():
    value = 1
    result = Success(Success(value))
    assert isinstance(result, Success)
    assert result.value == value


def test_eq():
    assert Success(1) == Success(1)


def test_eq_not_result():
    assert Failure(1).__eq__(1) == NotImplemented


def test_hash():
    assert hash(Success(1)) == hash(1)
