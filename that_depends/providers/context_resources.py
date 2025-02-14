import typing
import logging
import warnings
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from contextvars import ContextVar, Token
from types import TracebackType

from that_depends.providers.base import AbstractResource, ResourceContext


logger: typing.Final = logging.getLogger(__name__)
T = typing.TypeVar("T")
P = typing.ParamSpec("P")
_CONTAINER_CONTEXT: typing.Final[ContextVar[dict[str, typing.Any]]] = ContextVar("CONTAINER_CONTEXT")


class ContainerContext(AbstractAsyncContextManager[dict[str, typing.Any]], AbstractContextManager[dict[str, typing.Any]]):
    """Manage the context of ContextResources.\n\n    Can be entered using ``async with ContainerContext()`` or with ``with ContainerContext()``\n    as a async-context-manager or context-manager respectively.\n    When used as an async-context-manager, it will allow setup & teardown of both sync and async resources.\n    When used as an sync-context-manager, it will only allow setup & teardown of sync resources.\n    """

    def __init__(self, initial_context: dict[str, typing.Any] | None = None) -> None:
        self._initial_context: dict[str, typing.Any] = initial_context or {}
        self._context_token: Token[dict[str, typing.Any]] | None = None

    def __enter__(self) -> dict[str, typing.Any]:
        self._context_token = _CONTAINER_CONTEXT.set(self._initial_context)
        return _CONTAINER_CONTEXT.get()

    async def __aenter__(self) -> dict[str, typing.Any]:
        self._context_token = _CONTAINER_CONTEXT.set(self._initial_context)
        return _CONTAINER_CONTEXT.get()

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        if self._context_token is None:
            msg = "Context is not set, call ``__enter__`` first"
            raise RuntimeError(msg)
        _CONTAINER_CONTEXT.reset(self._context_token)

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, traceback: TracebackType | None
    ) -> None:
        if self._context_token is None:
            msg = "Context is not set, call ``__aenter__`` first"
            raise RuntimeError(msg)
        _CONTAINER_CONTEXT.reset(self._context_token)


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
        self._internal_name: typing.Final = f"{creator.__name__}-{typing.cast(str, typing.uuid4())}"

    def _fetch_context(self) -> ResourceContext[T]:
        container_context = _CONTAINER_CONTEXT.get()
        if self._internal_name not in container_context:
            container_context[self._internal_name] = ResourceContext(is_async=_is_container_context_async())
        return typing.cast(ResourceContext[T], container_context[self._internal_name])


class AsyncContextResource(ContextResource[T]):
    def __init__(
        self,
        creator: typing.Callable[P, typing.AsyncIterator[T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        warnings.warn("AsyncContextResource is deprecated, use ContextResource instead", RuntimeWarning, stacklevel=1)
        super().__init__(creator, *args, **kwargs)