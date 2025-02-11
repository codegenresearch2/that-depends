import typing

from that_depends.providers.base import AbstractProvider
from that_depends.providers.singleton import Singleton


T_co = typing.TypeVar("T_co", covariant=True)
P = typing.ParamSpec("P")


class Object(AbstractProvider[T_co]):
    __slots__ = ("_provider", "_override")

    def __init__(self, factory: typing.Callable[P, T_co], *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__()
        self._provider = Singleton(factory, *args, **kwargs)
        self._override = None

    async def async_resolve(self) -> T_co:
        return await self._provider.async_resolve()

    def sync_resolve(self) -> T_co:
        return self._provider.sync_resolve()

    def override(self, obj: T_co) -> None:
        self._override = obj

    async def async_override(self, obj: T_co) -> None:
        self._override = obj

    def clear_override(self) -> None:
        self._override = None

    async def async_clear_override(self) -> None:
        self._override = None