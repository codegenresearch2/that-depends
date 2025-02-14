import typing

from that_depends.providers.base import AbstractProvider
from that_depends.providers.singleton import Singleton


T_co = typing.TypeVar("T_co", covariant=True)
P = typing.ParamSpec("P")


class Object(AbstractProvider[T_co]):
    __slots__ = ("_obj",)

    def __init__(self, obj: T_co) -> None:
        super().__init__()
        self._obj: typing.Final = obj

    async def async_resolve(self) -> T_co:
        return self._obj

    def sync_resolve(self) -> T_co:
        return self._obj


class ConfigurableObject(AbstractProvider[T_co]):
    __slots__ = ("_factory", "_args", "_kwargs")

    def __init__(self, factory: typing.Callable[P, T_co], *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__()
        self._factory: typing.Final = factory
        self._args: typing.Final = args
        self._kwargs: typing.Final = kwargs

    async def async_resolve(self) -> T_co:
        return self._factory(
            *[await x.async_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],
            **{k: await v.async_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()}
        )

    def sync_resolve(self) -> T_co:
        return self._factory(
            *[x.sync_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],
            **{k: v.sync_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()}
        )


class SingletonObject(Singleton[T_co], AbstractProvider[T_co]):
    __slots__ = ("_factory", "_args", "_kwargs", "_override", "_instance")

    def __init__(self, factory: typing.Callable[P, T_co], *args: P.args, **kwargs: P.kwargs) -> None:
        Singleton.__init__(self, factory, *args, **kwargs)
        self._factory: typing.Final = factory
        self._args: typing.Final = args
        self._kwargs: typing.Final = kwargs
        self._instance: T_co | None = None

    async def async_resolve(self) -> T_co:
        return await Singleton.async_resolve(self)

    def sync_resolve(self) -> T_co:
        return Singleton.sync_resolve(self)