import typing

from that_depends.providers.base import AbstractProvider
from that_depends.providers.singleton import Singleton


T_co = typing.TypeVar("T_co", covariant=True)
P = typing.ParamSpec("P")


class Object(AbstractProvider[T_co]):
    __slots__ = ("_provider",)

    def __init__(self, provider: AbstractProvider[T_co]) -> None:
        super().__init__()
        self._provider: typing.Final = provider

    async def async_resolve(self) -> T_co:
        return await self._provider.async_resolve()

    def sync_resolve(self) -> T_co:
        return self._provider.sync_resolve()