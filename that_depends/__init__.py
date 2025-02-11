from that_depends.providers import container_context, fetch_context_item, sync_container_context
from that_depends.container import BaseContainer
from that_depends.injection import Provide, inject


async def container_context(context=None):
    async with container_context(context) as context_manager:
        yield context_manager
    await sync_container_context()


__all__ = [
    "container_context",
    "fetch_context_item",
    "sync_container_context",
    "BaseContainer",
    "inject",
    "Provide",
]