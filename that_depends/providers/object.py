import typing

from that_depends.providers.base import AbstractProvider
from that_depends.providers.singleton import Singleton


T_co = typing.TypeVar("T_co", covariant=True)
P = typing.ParamSpec("P")


class ObjectProvider(AbstractProvider[T_co]):
    __slots__ = ("_obj",)

    def __init__(self, obj: T_co) -> None:
        super().__init__()
        self._obj: typing.Final = obj

    async def async_resolve(self) -> T_co:
        return self._obj

    def sync_resolve(self) -> T_co:
        return self._obj


class ObjectFactory(AbstractProvider[T_co]):
    __slots__ = ("_factory", "_args", "_kwargs")

    def __init__(self, factory: typing.Callable[P, T_co], *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__()
        self._factory = factory
        self._args = args
        self._kwargs = kwargs

    async def async_resolve(self) -> T_co:
        return self._factory(
            *[await x.async_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],
            **{k: await v.async_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()},
        )

    def sync_resolve(self) -> T_co:
        return self._factory(
            *[x.sync_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],
            **{k: v.sync_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()},
        )