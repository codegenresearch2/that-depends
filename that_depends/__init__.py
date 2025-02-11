from that_depends import providers
from that_depends.container import BaseContainer
from that_depends.injection import Provide, inject
from that_depends.providers import fetch_context_item, sync_container_context


async def container_context(context):
    async with providers.container_context(context) as context_manager:
        yield context_manager
    await sync_container_context()


__all__ = [
    "fetch_context_item",
    "providers",
    "BaseContainer",
    "inject",
    "Provide",
    "sync_container_context",
]