import asyncio
from typing import Any, TypeVar

from that_depends.providers.base import AbstractProvider
from that_depends.providers.collections import Dict, List
from that_depends.providers.context_resources import (
    AsyncContextResource,
    ContextResource,
    DIContextMiddleware,
    container_context,
)
from that_depends.providers.factories import AsyncFactory, Factory
from that_depends.providers.object import Object
from that_depends.providers.resources import AsyncResource, Resource
from that_depends.providers.selector import Selector
from that_depends.providers.singleton import Singleton
from that_depends.providers.attr_getter import AttrGetter

T_co = TypeVar("T_co", covariant=True)

__all__ = [
    "AbstractProvider",
    "AsyncContextResource",
    "AsyncFactory",
    "AsyncResource",
    "AttrGetter",
    "ContextResource",
    "DIContextMiddleware",
    "Dict",
    "Factory",
    "List",
    "Object",
    "Resource",
    "Selector",
    "Singleton",
    "container_context",
]

class EnhancedAbstractProvider(AbstractProvider[T_co]):
    async def resolve(self) -> T_co:
        try:
            return await self.async_resolve()
        except Exception as e:
            raise RuntimeError(f"Failed to resolve {self.__class__.__name__}: {str(e)}") from e

class EnhancedDict(Dict[T_co]):
    async def resolve(self) -> dict[str, T_co]:
        try:
            return await self.async_resolve()
        except Exception as e:
            raise RuntimeError(f"Failed to resolve {self.__class__.__name__}: {str(e)}") from e

class EnhancedList(List[T_co]):
    async def resolve(self) -> list[T_co]:
        try:
            return await self.async_resolve()
        except Exception as e:
            raise RuntimeError(f"Failed to resolve {self.__class__.__name__}: {str(e)}") from e

async def main():
    provider = EnhancedDict(key1=EnhancedAbstractProvider(), key2=EnhancedAbstractProvider())
    result = await provider.resolve()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())


In the rewritten code, I have added `resolve` methods to `EnhancedAbstractProvider`, `EnhancedDict`, and `EnhancedList` classes to provide a common interface for resolving the providers. These methods use async methods for resolution and handle exceptions consistently. I have also added an example `main` function to demonstrate how to use the enhanced classes.