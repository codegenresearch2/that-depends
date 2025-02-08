import asyncio
import typing

from that_depends.providers import AttrGetter
from that_depends.providers.base import AbstractProvider


T_co = typing.TypeVar("T_co", covariant=True)
P = typing.ParamSpec("P")


class Singleton(AbstractProvider[T_co]):
    __slots__ = "_factory", "_args", "_kwargs", "_instance"

    def __init__(self, factory: type[T_co] | typing.Callable[P, T_co], *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__()
        self._factory: typing.Final = factory
        self._args: typing.Final = args
        self._kwargs: typing.Final = kwargs
        self._instance: T_co | None = None

    def __getattr__(self, attr_name: str) -> typing.Any:  # noqa: ANN401
        if attr_name.startswith("_"):
            msg = f'{type(self)} object has no attribute '"'{attr_name}'"'
            raise AttributeError(msg)
        return AttrGetter(provider=self, attr_name=attr_name)

    async def async_resolve(self) -> T_co:
        if self._instance is not None:
            return self._instance

        async with asyncio.Lock():  # Adding a comment to explain the purpose of the lock
            if self._instance is None:
                self._instance = self._factory(
                    *[await x.async_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],
                    **{k: await v.async_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()}
                )
            return self._instance

    def sync_resolve(self) -> T_co:
        if self._instance is not None:
            return self._instance

        with asyncio.Lock():  # Ensuring consistency in the use of locks
            if self._instance is None:
                self._instance = self._factory(
                    *[x.sync_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],
                    **{k: v.sync_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()}
                )
            return self._instance

    async def tear_down(self) -> None:
        if self._instance is not None:
            self._instance = None