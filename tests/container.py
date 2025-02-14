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
    def override_sync_resource(cls, new_resource: datetime.datetime) -> None:
        cls.sync_resource.override(lambda: typing.cast(typing.Iterator[datetime.datetime], iter([new_resource])))

    @classmethod
    def override_async_resource(cls, new_resource: datetime.datetime) -> None:
        cls.async_resource.override(lambda: typing.cast(typing.AsyncIterator[datetime.datetime], async_iter([new_resource])))

    @classmethod
    def override_simple_factory(cls, dep1: str, dep2: int) -> None:
        cls.simple_factory.override(lambda: SimpleFactory(dep1=dep1, dep2=dep2))

    @classmethod
    def override_async_factory(cls, now: datetime.datetime) -> None:
        cls.async_factory.override(lambda: async_factory(now))

    @classmethod
    def override_dependent_factory(cls, simple_factory: SimpleFactory, sync_resource: datetime.datetime, async_resource: datetime.datetime) -> None:
        cls.dependent_factory.override(lambda: DependentFactory(simple_factory=simple_factory, sync_resource=sync_resource, async_resource=async_resource))

    @classmethod
    def override_singleton(cls, dep1: bool) -> None:
        cls.singleton.override(lambda: SingletonFactory(dep1=dep1))

    @classmethod
    def get_sync_resource(cls) -> datetime.datetime:
        return next(cls.sync_resource())

    @classmethod
    def get_async_resource(cls) -> datetime.datetime:
        return next(cls.async_resource())

    @classmethod
    def get_simple_factory(cls) -> SimpleFactory:
        return cls.simple_factory()

    @classmethod
    def get_async_factory(cls) -> datetime.datetime:
        return cls.async_factory()

    @classmethod
    def get_dependent_factory(cls) -> DependentFactory:
        return cls.dependent_factory()

    @classmethod
    def get_singleton(cls) -> SingletonFactory:
        return cls.singleton()

    @classmethod
    def assert_sync_resource(cls) -> None:
        resource = cls.get_sync_resource()
        assert isinstance(resource, datetime.datetime)

    @classmethod
    def assert_async_resource(cls) -> None:
        resource = cls.get_async_resource()
        assert isinstance(resource, datetime.datetime)

    @classmethod
    def assert_simple_factory(cls) -> None:
        factory = cls.get_simple_factory()
        assert isinstance(factory, SimpleFactory)

    @classmethod
    def assert_async_factory(cls) -> None:
        factory = cls.get_async_factory()
        assert isinstance(factory, datetime.datetime)

    @classmethod
    def assert_dependent_factory(cls) -> None:
        factory = cls.get_dependent_factory()
        assert isinstance(factory, DependentFactory)

    @classmethod
    def assert_singleton(cls) -> None:
        factory = cls.get_singleton()
        assert isinstance(factory, SingletonFactory)