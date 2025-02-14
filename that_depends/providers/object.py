import typing

from that_depends.providers.base import AbstractProvider

T_co = typing.TypeVar("T_co", covariant=True)
P = typing.ParamSpec("P")

class Object(AbstractProvider[T_co]):
    __slots__ = ("_factory", "_args", "_kwargs")

    def __init__(self, factory: typing.Callable[P, T_co], *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__()
        self._factory: typing.Final = factory
        self._args: typing.Final = args
        self._kwargs: typing.Final = kwargs

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

In this rewritten code, the `Object` provider has been extended to accept a factory function and its arguments, similar to the `Singleton` provider. This allows for more flexibility in creating objects and maintaining consistency in resource handling. The `async_resolve` and `sync_resolve` methods have been updated to call the factory function with the resolved arguments, enabling the creation of objects from other providers. This change enhances test coverage with new objects, as the factory function can be mocked or stubbed in tests.