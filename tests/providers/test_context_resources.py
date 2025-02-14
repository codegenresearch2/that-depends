import datetime
import logging
import typing
import uuid
from contextlib import AsyncExitStack, ExitStack

import pytest

from that_depends import BaseContainer, fetch_context_item, providers
from that_depends.providers import container_context
from that_depends.providers.base import ResourceContext

logger = logging.getLogger(__name__)

def create_sync_context_resource() -> typing.Iterator[str]:
    logger.info("Resource initiated")
    yield f"sync {uuid.uuid4()}"
    logger.info("Resource destructed")

async def create_async_context_resource() -> typing.AsyncIterator[str]:
    logger.info("Async resource initiated")
    yield f"async {uuid.uuid4()}"
    logger.info("Async resource destructed")

class DIContainer(BaseContainer):
    @staticmethod
    def is_context_set() -> bool:
        return ResourceContext.get_context_stack() is not None

    @classmethod
    def init_sync_resource(cls):
        cls.sync_context_resource = providers.ContextResource(create_sync_context_resource)

    @classmethod
    def init_async_resource(cls):
        cls.async_context_resource = providers.ContextResource(create_async_context_resource)

    @classmethod
    def init_dynamic_resource(cls):
        cls.dynamic_context_resource = providers.Selector(
            lambda: fetch_context_item("resource_type") or "sync",
            sync=cls.sync_context_resource,
            async_=cls.async_context_resource,
        )

@pytest.fixture(autouse=True)
async def _clear_di_container() -> typing.AsyncIterator[None]:
    try:
        yield
    finally:
        await DIContainer.tear_down()

@pytest.fixture(params=[DIContainer.init_sync_resource, DIContainer.init_async_resource])
def context_resource(request: pytest.FixtureRequest) -> providers.ContextResource[str]:
    request.param()
    return DIContainer.sync_context_resource if request.param == DIContainer.init_sync_resource else DIContainer.async_context_resource

def test_context_resource_without_context_init(context_resource: providers.ContextResource[str]) -> None:
    if context_resource.is_async:
        with pytest.raises(RuntimeError, match="Context is not set. Use container_context"):
            await context_resource.async_resolve()
    else:
        with pytest.raises(RuntimeError, match="Context is not set. Use container_context"):
            context_resource.sync_resolve()

@container_context()
async def test_context_resource(context_resource: providers.ContextResource[str]) -> None:
    context_resource_result = await context_resource() if context_resource.is_async else context_resource.sync_resolve()
    assert await context_resource() is context_resource_result

@container_context()
def test_sync_context_resource(sync_context_resource: providers.ContextResource[str]) -> None:
    context_resource_result = sync_context_resource.sync_resolve()
    assert sync_context_resource.sync_resolve() is context_resource_result

async def test_async_context_resource_in_sync_context(async_context_resource: providers.ContextResource[str]) -> None:
    with pytest.raises(RuntimeError, match="AsyncResource cannot be resolved in an sync context."), container_context():
        await async_context_resource()

async def test_context_resource_different_context(context_resource: providers.ContextResource[datetime.datetime]) -> None:
    async with container_context():
        context_resource_instance1 = await context_resource()

    async with container_context():
        context_resource_instance2 = await context_resource()

    assert context_resource_instance1 is not context_resource_instance2

async def test_context_resource_included_context(context_resource: providers.ContextResource[datetime.datetime]) -> None:
    async with container_context():
        context_resource_instance1 = await context_resource()
        async with container_context():
            context_resource_instance2 = await context_resource()

        context_resource_instance3 = await context_resource()

    assert context_resource_instance1 is not context_resource_instance2
    assert context_resource_instance1 is context_resource_instance3

async def test_context_resources_overriding(context_resource: providers.ContextResource[str]) -> None:
    context_resource_mock = datetime.datetime.now(tz=datetime.timezone.utc)
    context_resource.override(context_resource_mock)

    context_resource_result = await context_resource() if context_resource.is_async else context_resource.sync_resolve()
    assert context_resource_result is context_resource_mock

    DIContainer.reset_override()
    with pytest.raises(RuntimeError, match="Context is not set. Use container_context"):
        await context_resource()

async def test_context_resources_init_and_tear_down() -> None:
    await DIContainer.init_resources()
    await DIContainer.tear_down()

def test_context_resources_wrong_providers_init() -> None:
    with pytest.raises(RuntimeError, match="ContextResource must be generator function"):
        providers.ContextResource(lambda: None)  # type: ignore[arg-type,return-value]

async def test_context_resource_with_dynamic_resource() -> None:
    DIContainer.init_dynamic_resource()
    async with container_context({"resource_type": "sync"}):
        assert (await DIContainer.dynamic_context_resource()).startswith("sync")

    async with container_context({"resource_type": "async_"}):
        assert (await DIContainer.dynamic_context_resource()).startswith("async")

    async with container_context():
        assert (await DIContainer.dynamic_context_resource()).startswith("sync")

async def test_early_exit_of_container_context() -> None:
    with pytest.raises(RuntimeError, match="Context is not set, call ``__aenter__`` first"):
        await container_context().__aexit__(None, None, None)
    with pytest.raises(RuntimeError, match="Context is not set, call ``__enter__`` first"):
        container_context().__exit__(None, None, None)

async def test_resource_context_early_teardown() -> None:
    context = ResourceContext(is_async=True)
    assert context.context_stack is None
    context.tear_down()
    assert context.context_stack is None

async def test_teardown_sync_container_context_with_async_resource() -> None:
    with pytest.raises(RuntimeError, match="Cannot tear down async context in sync mode"):
        ResourceContext(is_async=True, context_stack=AsyncExitStack()).tear_down()

async def test_creating_async_resource_in_sync_context() -> None:
    with pytest.raises(RuntimeError, match="Cannot use async resource in sync mode."):
        ResourceContext(is_async=False, context_stack=AsyncExitStack())