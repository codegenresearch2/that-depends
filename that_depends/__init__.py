from that_depends import providers
from that_depends.container import BaseContainer
from that_depends.injection import Provide, inject
from that_depends.providers import container_context, fetch_context_item, sync_container_context


class AsyncContextManager:
    async def __aenter__(self):
        # Context manager setup code
        pass

    async def __aexit__(self, exc_type, exc, tb):
        # Context manager teardown code
        pass


async def container_context(context=None):
    async with AsyncContextManager() as context_manager:
        yield context_manager
    await sync_container_context()


__all__ = [
    "providers",
    "container_context",
    "fetch_context_item",
    "sync_container_context",
    "BaseContainer",
    "inject",
    "Provide",
]