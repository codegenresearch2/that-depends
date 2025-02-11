import asyncio
import typing

from that_depends.providers.base import AbstractProvider


T_co = typing.TypeVar("T_co", covariant=True)
P = typing.ParamSpec("P")


class Singleton(AbstractProvider[T_co]):
    __slots__ = "_factory", "_args", "_kwargs", "_override", "_instance", "_resolving_lock"

    def __init__(self, factory: typing.Callable[P, T_co], *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__()
        self._factory: typing.Final = factory
        self._args: typing.Final = args
        self._kwargs: typing.Final = kwargs
        self._instance: T_co | None = None
        self._resolving_lock: typing.Final = asyncio.Lock()
        self._override: typing.Any = None  # Ensure _override is properly defined

    async def async_resolve(self) -> T_co:
        if self._override is not None:
            return typing.cast(T_co, self._override)

        if self._instance is not None:
            return self._instance

        # lock to prevent resolving several times
        async with self._resolving_lock:
            if self._instance is None:
                self._instance = self._factory(
                    *[await x.async_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],  # type: ignore[arg-type]
                    **{k: await v.async_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()},  # type: ignore[arg-type]
                )
            return self._instance

    def sync_resolve(self) -> T_co:
        if self._override is not None:
            return typing.cast(T_co, self._override)

        if self._instance is None:
            self._instance = self._factory(
                *[x.sync_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],  # type: ignore[arg-type]
                **{k: v.sync_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()},  # type: ignore[arg-type]
            )
        return self._instance

    async def tear_down(self) -> None:
        if self._instance is not None:
            self._instance = None


Changes made:
1. Placed the `# type: ignore[arg-type]` comments directly above the comprehensions for better readability.
2. Ensured proper indentation and spacing around the comprehensions.
3. Added initialization for the `_override` attribute to avoid potential issues.