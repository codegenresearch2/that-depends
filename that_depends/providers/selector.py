import typing

from that_depends.providers.base import AbstractProvider


T_co = typing.TypeVar("T_co", covariant=True)


class Selector(AbstractProvider[T_co]):
    __slots__ = "_selector", "_providers", "_override"

    def __init__(self, selector: typing.Callable[[], str], **providers: AbstractProvider[T_co]) -> None:
        super().__init__()
        self._selector: typing.Final = selector
        self._providers: typing.Final = providers
        self._override = None

    def __getattr__(self, attr_name: str) -> typing.Any:  # noqa: ANN401
        if attr_name in self._providers:
            return self._providers[attr_name]
        msg = f"'{type(self)}' object has no attribute '{attr_name}'"
        raise AttributeError(msg)

    async def async_resolve(self) -> T_co:
        selected_key: typing.Final = self._selector()
        if selected_key not in self._providers:
            msg = f"No provider matches {selected_key}"
            raise RuntimeError(msg)
        if self._override is not None:
            return typing.cast(T_co, self._override)
        provider = self._providers.get(selected_key)
        if provider is not None:
            return await provider.async_resolve()
        raise RuntimeError(f"No provider found for key: {selected_key}")

    def sync_resolve(self) -> T_co:
        selected_key: typing.Final = self._selector()
        if selected_key not in self._providers:
            msg = f"No provider matches {selected_key}"
            raise RuntimeError(msg)
        if self._override is not None:
            return typing.cast(T_co, self._override)
        provider = self._providers.get(selected_key)
        if provider is not None:
            return provider.sync_resolve()
        raise RuntimeError(f"No provider found for key: {selected_key}")