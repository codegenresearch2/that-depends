import typing

from that_depends.providers.base import AbstractProvider

T_co = typing.TypeVar("T_co", covariant=True)

class Object(AbstractProvider[T_co]):
    __slots__ = ("_obj", "_override")

    def __init__(self, obj: T_co) -> None:
        super().__init__()
        self._obj: T_co = obj
        self._override: T_co | None = None

    def override(self, obj: T_co) -> None:
        self._override = obj

    async def async_resolve(self) -> T_co:
        return self._override if self._override is not None else self._obj

    def sync_resolve(self) -> T_co:
        return self._override if self._override is not None else self._obj


In the rewritten code, I added an `override` method to allow the user to override the object provider in tests. This method sets the `_override` attribute to the provided object. The `async_resolve` and `sync_resolve` methods have been updated to return the overridden object if it exists, otherwise they return the original object. This ensures object consistency in assertions.