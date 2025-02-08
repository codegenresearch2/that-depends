import typing

from that_depends.providers.base import AbstractProvider


T_co = typing.TypeVar('T_co', covariant=True)


class Selector(AbstractProvider[T_co]):\n    __slots__ = '_selector', '_providers', '_override'\n\n    def __init__(self, selector: typing.Callable[[], str], **providers: AbstractProvider[T_co]) -> None:\n        super().__init__()\n        self._selector: typing.Final = selector\n        self._providers: typing.Final = providers\n        self._override = None\n\n    async def async_resolve(self) -> T_co:\n        if self._override is not None:\n            return typing.cast(T_co, self._override)\n\n        selected_key: typing.Final = self._selector()\n        if selected_key not in self._providers:\n            msg = f'No provider matches {selected_key}'\n            raise RuntimeError(msg)\n        return await self._providers[selected_key].async_resolve()\n\n    def sync_resolve(self) -> T_co:\n        if self._override is not None:\n            return typing.cast(T_co, self._override)\n\n        selected_key: typing.Final = self._selector()\n        if selected_key not in self._providers:\n            msg = f'No provider matches {selected_key}'\n            raise RuntimeError(msg)\n        return self._providers[selected_key].sync_resolve()\n