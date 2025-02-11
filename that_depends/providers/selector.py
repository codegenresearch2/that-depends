import typing

from that_depends.providers.base import AbstractProvider


T_co = typing.TypeVar("T_co", covariant=True)


class Selector(AbstractProvider[T_co]):
    __slots__ = "_selector", "_providers", "_selected_provider"

    def __init__(self, selector: typing.Callable[[], str], **providers: AbstractProvider[T_co]) -> None:
        super().__init__()
        self._selector: typing.Final = selector
        self._providers: typing.Final = providers
        self._selected_provider: AbstractProvider[T_co] | None = None

    def __getattr__(self, attr_name: str) -> typing.Any:  # noqa: ANN401
        if self._selected_provider is None:
            selected_key = self._selector()
            if selected_key not in self._providers:
                msg = f"No provider matches {selected_key}"
                raise RuntimeError(msg)
            self._selected_provider = self._providers[selected_key]
        try:
            return getattr(self._selected_provider, attr_name)
        except AttributeError:
            msg = f"'{type(self)}' object has no attribute '{attr_name}'"
            raise AttributeError(msg)

    async def async_resolve(self) -> T_co:
        if self._selected_provider is None:
            selected_key = self._selector()
            if selected_key not in self._providers:
                msg = f"No provider matches {selected_key}"
                raise RuntimeError(msg)
            self._selected_provider = self._providers[selected_key]
        return await self._selected_provider.async_resolve()

    def sync_resolve(self) -> T_co:
        if self._selected_provider is None:
            selected_key = self._selector()
            if selected_key not in self._providers:
                msg = f"No provider matches {selected_key}"
                raise RuntimeError(msg)
            self._selected_provider = self._providers[selected_key]
        return self._selected_provider.sync_resolve()