import typing

from that_depends.providers.base import AbstractProvider
from that_depends.providers.singleton import Singleton


T_co = typing.TypeVar("T_co", covariant=True)


class Object(AbstractProvider[T_co]):
    __slots__ = ("_obj", "_override")

    def __init__(self, obj: T_co) -> None:
        super().__init__()
        self._obj: typing.Final = obj
        self._override: T_co | None = None

    async def async_resolve(self) -> T_co:
        if self._override is not None:
            return self._override
        return self._obj

    def sync_resolve(self) -> T_co:
        if self._override is not None:
            return self._override
        return self._obj

    def override(self, obj: T_co) -> None:
        self._override = obj

    async def async_override(self, obj: T_co) -> None:
        self._override = obj

    def clear_override(self) -> None:
        self._override = None