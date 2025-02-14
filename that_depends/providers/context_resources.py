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

logger: typing.Final = logging.getLogger(__name__)
T = typing.TypeVar("T", covariant=True)
P = typing.ParamSpec("P")
_CONTAINER_CONTEXT: typing.Final[ContextVar[dict[str, typing.Any]]] = ContextVar("CONTAINER_CONTEXT")
AppType = typing.TypeVar("AppType")
Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]
Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]
ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]
_ASYNC_CONTEXT_KEY: typing.Final[str] = "__ASYNC_CONTEXT__"

ContextType = dict[str, typing.Any]

class container_context(AbstractAsyncContextManager[ContextType], AbstractContextManager[ContextType]):
    # ... rest of the class implementation remains the same ...

class DIContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app: typing.Final[ASGIApp] = app

    @container_context()
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        return await self.app(scope, receive, send)

def _get_container_context() -> dict[str, typing.Any]:
    try:
        return _CONTAINER_CONTEXT.get()
    except LookupError as exc:
        msg = "Context is not set. Use container_context"
        raise RuntimeError(msg) from exc

def _is_container_context_async() -> bool:
    return typing.cast(bool, _get_container_context().get(_ASYNC_CONTEXT_KEY, False))

def fetch_context_item(key: str, default: typing.Any = None) -> typing.Any:
    return _get_container_context().get(key, default)

class ContextResource(AbstractResource[T]):
    __slots__ = (
        "_is_async",
        "_creator",
        "_args",
        "_kwargs",
        "_override",
        "_internal_name",
    )

    def __init__(
        self,
        creator: typing.Callable[P, typing.Iterator[T] | typing.AsyncIterator[T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        super().__init__(creator, *args, **kwargs)
        self._internal_name: typing.Final[str] = f"{creator.__name__}-{uuid.uuid4()}"

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


In the provided code, I have made the following changes:

1. Added `covariant=True` to the `T` type variable in the `container_context` class to make it covariant for improved type safety and flexibility.
2. Added consistent type annotations to the `DIContextMiddleware` class.
3. Added a type annotation to the `app` attribute in the `DIContextMiddleware` class.
4. Added type annotations to the `fetch_context_item` function.
5. Added type annotations to the `ContextResource` and `AsyncContextResource` classes.
6. Added a type annotation to the `_internal_name` attribute in the `ContextResource` class.