from that_depends.providers.attr_getter import AttrGetter
from that_depends.providers.base import AbstractProvider
from that_depends.providers.collections import Dict, List
from that_depends.providers.context_resources import DIContextMiddleware, container_context
from that_depends.providers.factories import AsyncFactory, Factory
from that_depends.providers.object import Object
from that_depends.providers.resources import AsyncResource, Resource
from that_depends.providers.selector import Selector
from that_depends.providers.singleton import Singleton
from that_depends.injection import inject
from that_depends import providers

__all__ = [
    "AbstractProvider",
    "AsyncFactory",
    "AsyncResource",
    "AttrGetter",
    "Dict",
    "Factory",
    "List",
    "Object",
    "Resource",
    "Selector",
    "Singleton",
    "container_context",
    "inject",
    "providers",
]

@inject
class EnhancedDIContextMiddleware(DIContextMiddleware):
    def __init__(self, *resources):
        self.resources = resources

    def __enter__(self):
        for resource in self.resources:
            container_context.add(resource)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for resource in self.resources:
            container_context.remove(resource)

# Example usage
with EnhancedDIContextMiddleware(Resource1(), Resource2()):
    # Resources are automatically managed within the context
    pass

In this rewritten code, I have added a decorator `@inject` to simplify context management. The `EnhancedDIContextMiddleware` class is created to enhance context resource functionality and flexibility. It automatically adds and removes resources from the context when entering and exiting the context, respectively. This improves code readability and maintainability by simplifying the management of resources within the context.