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


class Selector(AbstractProvider[T_co]):
    __slots__ = ('_selector', '_providers', '_override')

    def __init__(self, selector: typing.Callable[[], str], **providers: AbstractProvider[T_co]) -> None:
        super().__init__()
        self._selector: typing.Final = selector
        self._providers: typing.Final = providers

    async def async_resolve(self) -> T_co:
        if self._override:
            return typing.cast(T_co, self._override)

        selected_key: typing.Final = self._selector()
        if selected_key not in self._providers:
            msg = f'No provider matches {selected_key}'
            raise RuntimeError(msg)
        return await self._providers[selected_key].async_resolve()

    def sync_resolve(self) -> T_co:
        if self._override:
            return typing.cast(T_co, self._override)

        selected_key: typing.Final = self._selector()
        if selected_key not in self._providers:
            msg = f'No provider matches {selected_key}'
            raise RuntimeError(msg)
        return self._providers[selected_key].sync_resolve()


class List(AbstractProvider[list[T_co]]):
    __slots__ = ('_providers',)

    def __init__(self, *providers: AbstractProvider[T_co]) -> None:
        super().__init__()
        self._providers: typing.Final = providers

    async def async_resolve(self) -> list[T_co]:
        return [await x.async_resolve() for x in self._providers]

    def sync_resolve(self) -> list[T_co]:
        return [x.sync_resolve() for x in self._providers]

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
