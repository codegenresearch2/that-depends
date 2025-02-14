import dataclasses
import datetime
import logging
import typing

from that_depends import BaseContainer, providers

logger = logging.getLogger(__name__)

def create_mock_sync_resource() -> typing.Iterator[datetime.datetime]:
    logger.debug("Mock sync resource initiated")
    try:
        yield datetime.datetime.now(tz=datetime.timezone.utc)
    finally:
        logger.debug("Mock sync resource destructed")

async def create_mock_async_resource() -> typing.AsyncIterator[datetime.datetime]:
    logger.debug("Mock async resource initiated")
    try:
        yield datetime.datetime.now(tz=datetime.timezone.utc)
    finally:
        logger.debug("Mock async resource destructed")

@dataclasses.dataclass(kw_only=True, slots=True)
class SimpleFactory:
    dep1: str
    dep2: int

async def async_factory(now: datetime.datetime) -> datetime.datetime:
    return now + datetime.timedelta(hours=1)

@dataclasses.dataclass(kw_only=True, slots=True)
class DependentFactory:
    simple_factory: SimpleFactory
    sync_resource: datetime.datetime
    async_resource: datetime.datetime

@dataclasses.dataclass(kw_only=True, slots=True)
class FreeFactory:
    dependent_factory: DependentFactory
    sync_resource: str

@dataclasses.dataclass(kw_only=True, slots=True)
class SingletonFactory:
    dep1: bool

class DIContainer(BaseContainer):
    mock_sync_resource = providers.Resource(create_mock_sync_resource)
    mock_async_resource = providers.Resource(create_mock_async_resource)

    sync_resource = mock_sync_resource
    async_resource = mock_async_resource

    simple_factory = providers.Factory(SimpleFactory, dep1="text", dep2=123)
    async_factory = providers.AsyncFactory(async_factory, async_resource.cast)
    dependent_factory = providers.Factory(
        DependentFactory,
        simple_factory=simple_factory.cast,
        sync_resource=sync_resource.cast,
        async_resource=async_resource.cast,
    )
    singleton = providers.Singleton(SingletonFactory, dep1=True)

    def override_sync_resource(self, resource: providers.Resource):
        self.sync_resource = resource
        self.dependent_factory = providers.Factory(
            DependentFactory,
            simple_factory=self.simple_factory.cast,
            sync_resource=self.sync_resource.cast,
            async_resource=self.async_resource.cast,
        )

    def override_async_resource(self, resource: providers.Resource):
        self.async_resource = resource
        self.dependent_factory = providers.Factory(
            DependentFactory,
            simple_factory=self.simple_factory.cast,
            sync_resource=self.sync_resource.cast,
            async_resource=self.async_resource.cast,
        )

    async def init_resources(self):
        sync_resource_instance = await self.sync_resource()
        self.sync_resource.sync_resolve = lambda: sync_resource_instance
        async_resource_instance = await self.async_resource()
        self.async_resource.sync_resolve = lambda: async_resource_instance

In this rewritten code, I added mock providers for sync and async resources. I also added override functionality for both sync and async resources in the DIContainer. The dependent_factory is recreated whenever the sync or async resource is overridden to ensure consistency between async and sync resolutions. Additionally, I added init_resources method to the DIContainer to initialize the sync and async resources and ensure consistency between async and sync resolutions.