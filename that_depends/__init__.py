from that_depends import providers
from that_depends.container import BaseContainer
from that_depends.injection import Provide, inject
from that_depends.providers import container_context, fetch_context_item, sync_container_context


def container_context(context):
    def context_manager():
        try:
            yield providers.container_context(context)
        finally:
            sync_container_context()
    return context_manager()


__all__ = [
    "container_context",
    "fetch_context_item",
    "providers",
    "BaseContainer",
    "inject",
    "Provide",
    "sync_container_context",
]