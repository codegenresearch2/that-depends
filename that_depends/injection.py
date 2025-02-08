import functools
import inspect
import typing
import warnings

from that_depends.providers import AbstractProvider


P = typing.ParamSpec("P")
T = typing.TypeVar("T")


def inject(func: typing.Callable[P, T]) -> typing.Callable[P, T]:
    if inspect.iscoroutinefunction(func):
        return typing.cast(typing.Callable[P, T], _inject_to_async(func))
    return _inject_to_sync(func)


def _inject_to_async(func: typing.Callable[P, typing.Coroutine[typing.Any, typing.Any, T]]) -> typing.Callable[P, typing.Coroutine[typing.Any, typing.Any, T]]:
    @functools.wraps(func)
    async def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        sig = inspect.signature(func)
        injected = False
        for param in sig.parameters.values():
            if param.name not in kwargs and isinstance(param.default, AbstractProvider):
                kwargs[param.name] = await param.default()
                injected = True
        if not injected:
            warnings.warn(
                "Expected injection, but nothing found. Remove @inject decorator.", RuntimeWarning, stacklevel=1
            )
        return await func(*args, **kwargs)
    return inner


def _inject_to_sync(func: typing.Callable[P, T]) -> typing.Callable[P, T]:
    @functools.wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        sig = inspect.signature(func)
        injected = False
        for param in sig.parameters.values():
            if param.name not in kwargs and isinstance(param.default, AbstractProvider):
                if param.name in kwargs:
                    raise RuntimeError(f"Injected arguments must not be redefined, {param.name=}")
                kwargs[param.name] = param.default.sync_resolve()
                injected = True
        if not injected:
            warnings.warn(
                "Expected injection, but nothing found. Remove @inject decorator.", RuntimeWarning, stacklevel=1
            )
        return func(*args, **kwargs)
    return inner


class ClassGetItemMeta(type):
    def __getitem__(cls, provider: AbstractProvider[T]) -> T:
        return typing.cast(T, provider)


class Provide(metaclass=ClassGetItemMeta): ...
