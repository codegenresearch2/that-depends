import dataclasses
import datetime
import logging
import typing

from that_depends import BaseContainer, providers


logger = logging.getLogger(__name__)


def create_sync_resource() -> typing.Iterator[datetime.datetime]:
    logger.debug("Resource initiated")
    try:
        yield datetime.datetime.now(tz=datetime.timezone.utc)
    finally:
        logger.debug("Resource destructed")


async def create_async_resource() -> typing.AsyncIterator[datetime.datetime]:
    logger.debug("Async resource initiated")
    try:
        yield datetime.datetime.now(tz=datetime.timezone.utc)
    finally:
        logger.debug("Async resource destructed")


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
    sync_resource = providers.Resource(create_sync_resource)
    async_resource = providers.Resource(create_async_resource)

    simple_factory = providers.Factory(SimpleFactory, dep1="text", dep2=123)
    async_factory = providers.AsyncFactory(async_factory, async_resource.cast)
    dependent_factory = providers.Factory(
        DependentFactory,
        simple_factory=simple_factory.cast,
        sync_resource=sync_resource.cast,
        async_resource=async_resource.cast,
    )
    singleton = providers.Singleton(SingletonFactory, dep1=True)

    @classmethod
    def override_sync_resource(cls) -> typing.Iterator[datetime.datetime]:
        logger.debug("Resource initiated")
        try:
            yield datetime.datetime.now(tz=datetime.timezone.utc)
        finally:
            logger.debug("Resource destructed")

    @classmethod
    def override_async_resource(cls) -> typing.AsyncIterator[datetime.datetime]:
        logger.debug("Async resource initiated")
        try:
            yield datetime.datetime.now(tz=datetime.timezone.utc)
        finally:
            logger.debug("Async resource destructed")

    @classmethod
    def override_simple_factory(cls) -> SimpleFactory:
        return SimpleFactory(dep1="text", dep2=123)

    @classmethod
    def override_async_factory(cls) -> typing.Callable[[datetime.datetime], typing.Coroutine[typing.Any, typing.Any, datetime.datetime]]:
        return async_factory

    @classmethod
    def override_dependent_factory(cls) -> DependentFactory:
        return DependentFactory(
            simple_factory=cls.override_simple_factory(),
            sync_resource=next(cls.override_sync_resource()),
            async_resource=next(cls.override_async_resource()),
        )

    @classmethod
    def override_singleton(cls) -> SingletonFactory:
        return SingletonFactory(dep1=True)

    sync_resource = providers.Resource(override_sync_resource)
    async_resource = providers.Resource(override_async_resource)
    simple_factory = providers.Factory(override_simple_factory)
    async_factory = providers.AsyncFactory(override_async_factory, async_resource.cast)
    dependent_factory = providers.Factory(override_dependent_factory)
    singleton = providers.Singleton(override_singleton)