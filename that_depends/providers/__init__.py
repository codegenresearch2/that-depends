from that_depends import inject, Provide
from that_depends.providers import Dict, List, container_context, sync_container_context, fetch_context_item
from that_depends.providers.base import AbstractProvider
from that_depends.providers.context_resources import DIContextMiddleware

__all__ = [
    "AbstractProvider",
    "Dict",
    "List",
    "DIContextMiddleware",
    "container_context",
    "sync_container_context",
    "fetch_context_item",
    "inject",
    "Provide",
]

# Example of using decorators for context management
@inject
def my_function(resource: AbstractProvider):
    # Use the resource here
    pass

# Example of enhancing context resource functionality with a decorator
@Provide(resource_name="my_resource")
def create_resource():
    # Create and return the resource
    pass

# Example of improving code readability and maintainability
async def get_resources():
    # Using List and Dict providers for better resource management
    resources = await List(
        fetch_context_item("resource1"),
        fetch_context_item("resource2")
    ).async_resolve()

    config = await Dict(
        db_config=fetch_context_item("db_config"),
        app_config=fetch_context_item("app_config")
    ).async_resolve()

    return resources, config