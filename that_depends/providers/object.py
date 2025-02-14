import typing

from that_depends.providers.base import AbstractProvider

T_co = typing.TypeVar("T_co", covariant=True)

class Object(AbstractProvider[T_co]):
    __slots__ = ("_provider",)

    def __init__(self, provider: AbstractProvider[T_co]) -> None:
        super().__init__()
        self._provider: typing.Final = provider

    async def async_resolve(self) -> T_co:
        return await self._provider.async_resolve()

    def sync_resolve(self) -> T_co:
        return self._provider.sync_resolve()


In the rewritten code, the `Object` class now takes an `AbstractProvider` instance as a parameter instead of a generic object. This allows for more flexibility in resource handling as the user can now provide any type of provider that implements the `AbstractProvider` interface. This also maintains consistency in resource handling as all providers follow the same interface. Additionally, this change enhances test coverage as it allows for the creation of mock providers for testing purposes.