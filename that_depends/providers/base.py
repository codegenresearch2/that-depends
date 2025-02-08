import abc
import asyncio
import contextlib
import inspect
import typing
from contextlib import contextmanager


T_co = typing.TypeVar("T_co", covariant=True)
R = typing.TypeVar("R")
P = typing.ParamSpec("P")


class AbstractProvider(typing.Generic[T_co], abc.ABC):
    """Abstract Provider Class."""

    def __init__(self) -> None:
        super().__init__()
        self._override: typing.Any = None

    @abc.abstractmethod
    async def async_resolve(self) -> T_co:
        """Resolve dependency asynchronously."""

    @abc.abstractmethod
    def sync_resolve(self) -> T_co:
        """Resolve dependency synchronously."""

    async def __call__(self) -> T_co:
        return await self.async_resolve()

    def override(self, mock: object) -> None:
        self._override = mock

    @contextmanager
    def override_context(self, mock: object) -> typing.Iterator[None]:
        self.override(mock)
        try:
            yield
        finally:
            self.reset_override()

    def reset_override(self) -> None:
        self._override = None

    @property
    def cast(self) -> T_co:
        """Returns self, but cast to the type of the provided value."""
        return typing.cast(T_co, self)

    def __getattr__(self, name: str) -> typing.Any:
        """Allows for dynamic attribute access."
        raise AttributeError(f'\'{type(self).__name__}' object has no attribute '\'{name}\'') from None


class ResourceContext(typing.Generic[T_co]):
    __slots__ = "context_stack", "instance", "resolving_lock", "is_async"

    def __init__(self, is_async: bool) -> None:
        """Create a new ResourceContext instance."
        self.instance: T_co | None = None
        self.resolving_lock: typing.Final = asyncio.Lock()
        self.context_stack: contextlib.AsyncExitStack | contextlib.ExitStack | None = None
        self.is_async = is_async

    @staticmethod
    def is_context_stack_async(
        context_stack: contextlib.AsyncExitStack | contextlib.ExitStack | None,
    ) -> typing.TypeGuard[contextlib.AsyncExitStack]:
        return isinstance(context_stack, contextlib.AsyncExitStack)

    @staticmethod
    def is_context_stack_sync(
        context_stack: contextlib.AsyncExitStack | contextlib.ExitStack,
    ) -> typing.TypeGuard[contextlib.ExitStack]:
        return isinstance(context_stack, contextlib.ExitStack)

    async def tear_down(self) -> None:
        """Async tear down the context stack."""
        if self.context_stack is None:
            return

        if self.is_context_stack_async(self.context_stack):
            await self.context_stack.aclose()
        elif self.is_context_stack_sync(self.context_stack):
            self.context_stack.close()
        self.context_stack = None
        self.instance = None

    def sync_tear_down(self) -> None:
        """Sync tear down the context stack."
        if self.context_stack is None:
            return

        if self.is_context_stack_sync(self.context_stack):
            self.context_stack.close()
            self.context_stack = None
            self.instance = None
        elif self.is_context_stack_async(self.context_stack):
            msg = "Cannot tear down async context in sync mode"
            raise RuntimeError(msg)
