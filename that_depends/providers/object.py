import typing

from that_depends.providers.base import AbstractProvider
from that_depends.providers.singleton import Singleton


T_co = typing.TypeVar("T_co", covariant=True)


class Object(AbstractProvider[T_co]):
    __slots__ = ("_obj",)

    def __init__(self, obj: T_co) -> None:
        super().__init__()
        self._obj: typing.Final = obj

    async def async_resolve(self) -> T_co:
        return self._obj

    def sync_resolve(self) -> T_co:
        return self._obj