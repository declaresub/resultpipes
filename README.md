

# ResultPipes

ResultPipes is a library offering a Result generic type, and some decorators and operators that allow one
to chain sequences of callables that take one argument and return a Result.



## Compatibility

ResultPipes requires Python 3.10 or later, mostly due to the use of match statments.  


## Installation

Install from github:

    pip install pip@git+https://github.com/declaresub/resultpipes


## Usage
Right now, this project is mostly for my own use.  I will likely add it to PyPi along with all other such packages.  
Until then, here is a bit of documentation.

The Result part of ResultPipes is a Result generic type rather like those found in Swift, Rust, etc.  
The idea is that functions should return a Result type, which one can then match by type.

We have two classes, Success[S] and Failure[E].  Then the Result type is defined to be the union of these:

    Resul[S, E] = Success[S] | Failure[E]


Pipe functionality is enabled by a decorator, pipeable. it works for callables, including async.
A callable to be piped must have one positional parameter, and return Result[S, E].  The decorator
returns either a Pipeable, or an APipeable, if the callable decorated is async.

    @pipeable
    def f(x: int) -> Result[str, Error];
        ...

There are three pipe operators, |, &, ^ that operate on Pipeable | APipeable objects.

f | g:  if f returns a Success, then the return value is unwrapped and passed to g. If f returns a Failure, then that value is
piped along.
     
f & g: if f returns a Failure, then the return value is unwrapped and passed to g. If f returns a Success, then that value is
piped along.

f ^ g: this is essentially composition; the return value of f is passed to g.

Finally, there are two decorators catch, acatch that allow one to catch exceptions, log, report, etc, and then
return a Result. 

Each decorator takes a handler argument; the default action is to log the exception, then return a Failure[Exception]. 
I often use these decorators to wrap third-party functions.

I have so far resisted entering the monad rabbit hole; that may be version 1.


## Testing

The requirements.txt file is for development and testing. If you have any interest in either,
create a virtual environment and install this package.  The following may work.

    python -m venv /path/to/virtual-environment
    cd /path/to/virtual-environment
    source bin/activate
    pushd /path/to/repository
    pip install -r requirements.txt


Run unit tests:

    pytest --cov=src --cov-report term-missing tests

Or

    tox
