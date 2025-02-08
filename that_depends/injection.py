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


async def _inject_to_async(func: typing.Callable[P, typing.Coroutine[typing.Any, typing.Any, T]]) -> typing.Callable[P, typing.Coroutine[typing.Any, typing.Any, T]]:
    @functools.wraps(func)
    async def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        sig = inspect.signature(func)
        injected = False
        for param_name, param in sig.parameters.items():
            if param_name in kwargs:
                continue
            if isinstance(param.default, AbstractProvider):
                kwargs[param_name] = await param.default.async_resolve()
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
        for param_name, param in sig.parameters.items():
            if param_name in kwargs:
                if isinstance(param.default, AbstractProvider):
                    msg = f"Injected arguments must not be redefined, {param_name=}"
                    raise RuntimeError(msg)
                continue
            if isinstance(param.default, AbstractProvider):
                kwargs[param_name] = param.default.sync_resolve()
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