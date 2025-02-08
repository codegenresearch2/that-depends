import typing

from that_depends.providers.base import AbstractProvider

T_co = typing.TypeVar('T_co', covariant=True)

P = typing.ParamSpec('P')

class Object(AbstractProvider[T_co]):
    __slots__ = ('_obj',)

    def __init__(self, obj: T_co) -> None:
        super().__init__()
        self._obj: typing.Final = obj

    async def async_resolve(self) -> T_co:
        return self._obj

    def sync_resolve(self) -> T_co:
        return self._obj

    def __getattr__(self, attr_name: str) -> typing.Any:
        raise AttributeError(f'{self.__class__.__name__} object has no attribute {attr_name}')


class Selector(AbstractProvider[T_co]):
    __slots__ = ('_selector', '_providers')

    def __init__(self, selector: typing.Callable[[], str], **providers: AbstractProvider[T_co]) -> None:
        super().__init__()
        self._selector: typing.Final = selector
        self._providers: typing.Final = providers

    async def async_resolve(self) -> T_co:
        selected_key: typing.Final = self._selector()
        if selected_key not in self._providers:
            msg = f'No provider matches {selected_key}'  # noqa: ANN401
            raise RuntimeError(msg)
        return await self._providers[selected_key].async_resolve()

    def sync_resolve(self) -> T_co:
        selected_key: typing.Final = self._selector()
        if selected_key not in self._providers:
            msg = f'No provider matches {selected_key}'  # noqa: ANN401
            raise RuntimeError(msg)
        return self._providers[selected_key].sync_resolve()

    def __getattr__(self, attr_name: str) -> typing.Any:
        raise AttributeError(f'{self.__class__.__name__} object has no attribute {attr_name}')


class List(AbstractProvider[list[T_co]]):
    __slots__ = ('_providers',)

    def __init__(self, *providers: AbstractProvider[T_co]) -> None:
        super().__init__()
        self._providers: typing.Final = providers

    async def async_resolve(self) -> list[T_co]:
        return [await x.async_resolve() for x in self._providers]

    def sync_resolve(self) -> list[T_co]:
        return [x.sync_resolve() for x in self._providers]

    def __getattr__(self, attr_name: str) -> typing.Any:
        raise AttributeError(f'{self.__class__.__name__} object has no attribute {attr_name}')

    async def __call__(self) -> list[T_co]:
        return await self.async_resolve()


class Dict(AbstractProvider[dict[str, T_co]]):
    __slots__ = ('_providers',)

    def __init__(self, **providers: AbstractProvider[T_co]) -> None:
        super().__init__()
        self._providers: typing.Final = providers

    async def async_resolve(self) -> dict[str, T_co]:
        return {key: await provider.async_resolve() for key, provider in self._providers.items()}

    def sync_resolve(self) -> dict[str, T_co]:
        return {key: provider.sync_resolve() for key, provider in self._providers.items()}

    def __getattr__(self, attr_name: str) -> typing.Any:
        raise AttributeError(f'{self.__class__.__name__} object has no attribute {attr_name}')

    async def __call__(self) -> dict[str, T_co]:
        return await self.async_resolve()
