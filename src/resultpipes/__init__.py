from importlib.metadata import PackageNotFoundError, metadata

from .catch import acatch, catch
from .pipe import APipeable, Pipeable, failure, pipeable, success
from .result import Failure, Result, Success

__all__ = [
    "Result",
    "Success",
    "Failure",
    "Pipeable",
    "APipeable",
    "pipeable",
    "acatch",
    "success",
    "failure",
    "catch",
]

try:
    __version__: str = metadata(__name__)["version"]
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = ""
