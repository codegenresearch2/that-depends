import typing
import logging

from that_depends.providers.base import AbstractProvider

T_co = typing.TypeVar("T_co", covariant=True)

class ObjectProvider(AbstractProvider[T_co]):
    __slots__ = ("_obj",)

    def __init__(self, obj: T_co) -> None:
        super().__init__()
        self._obj: typing.Final = obj
        logging.info(f"ObjectProvider initialized with object: {obj}")

    async def async_resolve(self) -> T_co:
        logging.info(f"Resolving object asynchronously: {self._obj}")
        return self._obj

    def sync_resolve(self) -> T_co:
        logging.info(f"Resolving object synchronously: {self._obj}")
        return self._obj


In the rewritten code, I have renamed the class to `ObjectProvider` for better clarity and to follow the naming convention of other provider classes. I have also added logging statements to maintain consistent logging practices as per the user's preference. The logging statements provide information about the initialization of the provider and the resolution of the object.