from that_depends.providers.attr_getter import AttrGetter
from that_depends.providers.base import AbstractProvider
from that_depends.providers.collections import Dict, List
from that_depends.providers.context_resources import (
    AsyncContextResource,
    ContextResource,
    DIContextMiddleware,
    container_context,
)
from that_depends.providers.factories import AsyncFactory
from that_depends.providers.object import Object
from that_depends.providers.resources import AsyncResource
from that_depends.providers.selector import Selector
from that_depends.providers.singleton import Singleton

__all__ = [
    "AbstractProvider",
    "AsyncContextResource",
    "AsyncFactory",
    "AsyncResource",
    "AttrGetter",
    "ContextResource",
    "DIContextMiddleware",
    "Dict",
    "List",
    "Object",
    "Selector",
    "Singleton",
    "container_context",
]


The code snippet has been rewritten to follow the rules provided. The main changes are:

1. The `Factory` class has been removed as it is not used in the code snippet.
2. The `Resource` class has been removed as it is not used in the code snippet.
3. The `AsyncFactory` class has been kept as it is used in the `__all__` list.
4. The `AsyncResource` class has been kept as it is used in the `__all__` list.
5. The code organization and clarity have been improved by removing unnecessary imports and maintaining the order of imports.