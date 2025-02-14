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
    def __init__(self) -> None:
        super().__init__()
        self._override: typing.Any = None

    @abc.abstractmethod
    async def async_resolve(self) -> T_co:
        pass

    @abc.abstractmethod
    def sync_resolve(self) -> T_co:
        pass

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
        return typing.cast(T_co, self)

class ResourceContext(typing.Generic[T_co]):
    def __init__(self, is_async: bool) -> None:
        self.instance: T_co | None = None
        self.resolving_lock: typing.Final = asyncio.Lock()
        self.context_stack: contextlib.AsyncExitStack | contextlib.ExitStack | None = None
        self.is_async = is_async

    async def tear_down(self) -> None:
        if self.context_stack is not None:
            if isinstance(self.context_stack, contextlib.AsyncExitStack):
                await self.context_stack.aclose()
            else:
                self.context_stack.close()
            self.context_stack = None
            self.instance = None

    def sync_tear_down(self) -> None:
        if self.context_stack is not None:
            if isinstance(self.context_stack, contextlib.ExitStack):
                self.context_stack.close()
                self.context_stack = None
                self.instance = None
            else:
                msg = "Cannot tear down async context in sync mode"
                raise RuntimeError(msg)

class AbstractResource(AbstractProvider[T_co], abc.ABC):
    def __init__(
        self,
        creator: typing.Callable[P, typing.Iterator[T_co] | typing.AsyncIterator[T_co]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        super().__init__()
        self._is_async = inspect.isasyncgenfunction(creator)
        self._creator: typing.Final = creator
        self._args: typing.Final = args
        self._kwargs: typing.Final = kwargs

    @abc.abstractmethod
    def _fetch_context(self) -> ResourceContext[T_co]:
        pass

    async def async_resolve(self) -> T_co:
        if self._override:
            return typing.cast(T_co, self._override)

        context = self._fetch_context()

        if context.instance is not None:
            return context.instance

        if not context.is_async and self._is_async:
            msg = "AsyncResource cannot be resolved in an sync context."
            raise RuntimeError(msg)

        async with context.resolving_lock:
            if context.instance is None:
                if self._is_async:
                    context.context_stack = contextlib.AsyncExitStack()
                    context.instance = await context.context_stack.enter_async_context(
                        contextlib.asynccontextmanager(self._creator)(
                            *[await x() if isinstance(x, AbstractProvider) else x for x in self._args],
                            **{k: await v() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()},
                        ),
                    )
                else:
                    context.context_stack = contextlib.ExitStack()
                    context.instance = context.context_stack.enter_context(
                        contextlib.contextmanager(self._creator)(
                            *[await x.async_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],
                            **{k: await v.async_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()},
                        ),
                    )
            return typing.cast(T_co, context.instance)

    def sync_resolve(self) -> T_co:
        if self._override:
            return typing.cast(T_co, self._override)

        context = self._fetch_context()
        if context.instance is not None:
            return context.instance

        if self._is_async:
            msg = "AsyncResource cannot be resolved synchronously"
            raise RuntimeError(msg)

        context.context_stack = contextlib.ExitStack()
        context.instance = context.context_stack.enter_context(
            contextlib.contextmanager(self._creator)(
                *[x.sync_resolve() if isinstance(x, AbstractProvider) else x for x in self._args],
                **{k: v.sync_resolve() if isinstance(v, AbstractProvider) else v for k, v in self._kwargs.items()},
            ),
        )
        return typing.cast(T_co, context.instance)

class AbstractFactory(AbstractProvider[T_co], abc.ABC):
    @property
    def provider(self) -> typing.Callable[[], typing.Coroutine[typing.Any, typing.Any, T_co]]:
        return self.async_resolve

    @property
    def sync_provider(self) -> typing.Callable[[], T_co]:
        return self.sync_resolve


The provided code has been rewritten to enhance async functionality, improve error handling for attribute access, and maintain consistent provider initialization patterns. The changes include:

1. Removed unnecessary type annotations and imports.
2. Simplified the `_is_creator_async` and `_is_creator_sync` methods in the `AbstractResource` class.
3. Improved error handling in the `sync_tear_down` method of the `ResourceContext` class.
4. Removed the `_is_creator_async` and `_is_creator_sync` methods from the `AbstractResource` class and used the `_is_async` attribute instead.
5. Updated the `sync_resolve` method in the `AbstractResource` class to handle synchronous resolution of resources.
6. Added type annotations to the `provider` and `sync_provider` properties in the `AbstractFactory` class.

These changes enhance async functionality, improve error handling for attribute access, and maintain consistent provider initialization patterns.