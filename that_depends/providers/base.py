import abc
import asyncio
import contextlib
import inspect
import typing
from contextlib import contextmanager

T_co = typing.TypeVar("T_co", covariant=True)
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
    def __init__(self, creator: typing.Callable[P, typing.Iterator[T_co] | typing.AsyncIterator[T_co]], *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__()
        self._is_async = inspect.isasyncgenfunction(creator)
        self._creator = creator
        self._args = args
        self._kwargs = kwargs

    @abc.abstractmethod
    def _fetch_context(self) -> ResourceContext[T_co]:
        pass

    async def async_resolve(self) -> T_co:
        if self._override:
            return typing.cast(T_co, self._override)

        context = self._fetch_context()

        if context.instance is not None:
            return context.instance

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