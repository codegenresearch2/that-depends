import inspect
import logging
import typing
import uuid
import warnings
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from contextvars import ContextVar, Token
from functools import wraps
from types import TracebackType

from that_depends.providers.base import AbstractResource, ResourceContext

# Consolidate imports for clarity
from that_depends.providers.resources import Resource

logger = logging.getLogger(__name__)
T = typing.TypeVar("T")
P = typing.ParamSpec("P")
_CONTAINER_CONTEXT = ContextVar("CONTAINER_CONTEXT")
AppType = typing.TypeVar("AppType")
Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]
Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]
ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]
_ASYNC_CONTEXT_KEY = "__ASYNC_CONTEXT__"

ContextType = dict[str, typing.Any]

class sync_container_context(AbstractContextManager[ContextType]):
    """Manage the context of ContextResources for synchronous tests."""

    def __init__(self, initial_context: ContextType | None = None) -> None:
        self._initial_context: ContextType = initial_context or {}
        self._context_token: Token[ContextType] | None = None

    def __enter__(self) -> ContextType:
        self._initial_context[_ASYNC_CONTEXT_KEY] = False
        return self._enter()

    def _enter(self) -> ContextType:
        self._context_token = _CONTAINER_CONTEXT.set(self._initial_context or {})
        return _CONTAINER_CONTEXT.get()

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        if self._context_token is None:
            msg = "Context is not set, call ``__enter__`` first"
            raise RuntimeError(msg)

        try:
            for context_item in reversed(_CONTAINER_CONTEXT.get().values()):
                if isinstance(context_item, ResourceContext):
                    context_item.sync_tear_down()
        finally:
            _CONTAINER_CONTEXT.reset(self._context_token)

def _get_container_context() -> dict[str, typing.Any]:
    try:
        return _CONTAINER_CONTEXT.get()
    except LookupError as exc:
        msg = "Context is not set. Use sync_container_context for synchronous tests."
        raise RuntimeError(msg) from exc

def _is_container_context_async() -> bool:
    return typing.cast(bool, _get_container_context().get(_ASYNC_CONTEXT_KEY, False))

def fetch_context_item(key: str, default: typing.Any = None) -> typing.Any:
    return _get_container_context().get(key, default)

class ContextResource(Resource[T]):
    def __init__(
        self,
        creator: typing.Callable[P, typing.Iterator[T] | typing.AsyncIterator[T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        super().__init__(creator, *args, **kwargs)
        self._internal_name: typing.Final = f"{creator.__name__}-{uuid.uuid4()}"

    def _fetch_context(self) -> ResourceContext[T]:
        container_context = _get_container_context()
        if resource_context := container_context.get(self._internal_name):
            return typing.cast(ResourceContext[T], resource_context)

        resource_context = ResourceContext(is_async=_is_container_context_async())
        container_context[self._internal_name] = resource_context
        return resource_context

class AsyncContextResource(ContextResource[T]):
    def __init__(
        self,
        creator: typing.Callable[P, typing.AsyncIterator[T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        warnings.warn("AsyncContextResource is deprecated, use ContextResource instead", RuntimeWarning, stacklevel=1)
        super().__init__(creator, *args, **kwargs)

class DIContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app: typing.Final = app

    @sync_container_context()
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        return await self.app(scope, receive, send)


In this rewritten code, I have consolidated the imports for clarity, replaced `container_context` with `sync_container_context` for synchronous tests, and improved error messages for better debugging. The `ContextResource` and `AsyncContextResource` classes have been updated to use the `Resource` class from the `resources` module.