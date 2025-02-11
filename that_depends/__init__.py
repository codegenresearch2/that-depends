from that_depends import providers
from that_depends.container import BaseContainer
from that_depends.injection import Provide, inject
from that_depends.providers import container_context
from contextlib import asynccontextmanager


@asynccontextmanager
async def container_context():
    try:
        yield providers.container_context()
    finally:
        await providers.sync_container_context()


__all__ = [
    "container_context",
    "fetch_context_item",
    "providers",
    "BaseContainer",
    "inject",
    "Provide",
]