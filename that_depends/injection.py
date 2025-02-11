import functools
import inspect
import typing
import warnings

from that_depends.providers import AbstractProvider


P = typing.ParamSpec("P")
T = typing.TypeVar("T")


def inject(
    func: typing.Callable[P, T],
) -> typing.Callable[P, T]:
    if inspect.iscoroutinefunction(func):
        return typing.cast(typing.Callable[P, T], _inject_to_async(func))

    return _inject_to_sync(func)


def _inject_to_async(
    func: typing.Callable[P, typing.Coroutine[typing.Any, typing.Any, T]],
) -> typing.Callable[P, typing.Coroutine[typing.Any, typing.Any, T]]:
    signature = inspect.signature(func)

    @functools.wraps(func)
    async def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        for field_name, field_value in signature.parameters.items():
            if isinstance(field_value.default, AbstractProvider):
                if field_name not in kwargs:
                    kwargs[field_name] = await field_value.default()
        if not kwargs:
            warnings.warn(
                "Expected injection, but nothing found. Remove @inject decorator.", RuntimeWarning, stacklevel=1
            )
        return await func(*args, **kwargs)

    return inner


def _inject_to_sync(
    func: typing.Callable[P, T],
) -> typing.Callable[P, T]:
    signature = inspect.signature(func)

    @functools.wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        for field_name, field_value in signature.parameters.items():
            if isinstance(field_value.default, AbstractProvider):
                if field_name not in kwargs:
                    kwargs[field_name] = field_value.default.sync_resolve()
        if not kwargs:
            warnings.warn(
                "Expected injection, but nothing found. Remove @inject decorator.", RuntimeWarning, stacklevel=1
            )
        return func(*args, **kwargs)

    return inner


class ClassGetItemMeta(type):
    def __getitem__(cls, provider: AbstractProvider[T]) -> T:
        return typing.cast(T, provider)


class Provide(metaclass=ClassGetItemMeta): ...