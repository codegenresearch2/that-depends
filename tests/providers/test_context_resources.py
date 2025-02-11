import pytest
import datetime
import uuid
import typing
from contextlib import AsyncExitStack
import logging

from that_depends import BaseContainer, fetch_context_item, providers
from that_depends.providers import container_context, sync_container_context
from that_depends.providers.base import ResourceContext

# Import the logging module
logging.basicConfig()
logger = logging.getLogger(__name__)

# Store the generated UUIDs
sync_uuid = None
async_uuid = None

def create_sync_context_resource() -> typing.Iterator[str]:
    global sync_uuid
    logger.info("Resource initiated")
    sync_uuid = f"sync {uuid.uuid4()}"
    yield sync_uuid
    logger.info("Resource destructed")

async def create_async_context_resource() -> typing.AsyncIterator[str]:
    global async_uuid
    logger.info("Async resource initiated")
    async_uuid = f"async {uuid.uuid4()}"
    yield async_uuid
    logger.info("Async resource destructed")

class DIContainer(BaseContainer):
    sync_context_resource = providers.ContextResource(create_sync_context_resource)
    async_context_resource = providers.ContextResource(create_async_context_resource)
    dynamic_context_resource = providers.Selector(
        lambda: fetch_context_item("resource_type") or "sync",
        sync=sync_context_resource,
        async_=async_context_resource,
    )

@pytest.fixture(autouse=True)
async def _clear_di_container() -> typing.AsyncIterator[None]:
    try:
        yield
    finally:
        await DIContainer.tear_down()

@pytest.fixture
def sync_context_resource() -> providers.ContextResource[str]:
    return DIContainer.sync_context_resource

@pytest.fixture
def async_context_resource() -> providers.ContextResource[str]:
    return DIContainer.async_context_resource

@sync_container_context()
def test_sync_context_resource(sync_context_resource: providers.ContextResource[str]) -> None:
    global sync_uuid
    context_resource_result = sync_context_resource.sync_resolve()
    assert context_resource_result is sync_uuid

@container_context()
async def test_context_resource(context_resource: providers.ContextResource[str]) -> None:
    global sync_uuid
    context_resource_result = await context_resource()
    assert context_resource_result is sync_uuid

@container_context()
async def test_async_context_resource_in_sync_context(async_context_resource: providers.ContextResource[str]) -> None:
    with pytest.raises(RuntimeError, match="AsyncResource cannot be resolved in an sync context."):
        await async_context_resource()

@container_context()
def test_early_exit_of_container_context() -> None:
    with pytest.raises(RuntimeError, match="Context is not set, call ``__aexit__`` first"):
        container_context().__aexit__(None, None, None)
    with pytest.raises(RuntimeError, match="Context is not set, call ``__exit__`` first"):
        container_context().__exit__(None, None, None)

def test_resource_context_early_teardown() -> None:
    context: ResourceContext[str] = ResourceContext(is_async=True)
    assert context.context_stack is None
    context.sync_tear_down()
    assert context.context_stack is None

@pytest.mark.asyncio
async def test_teardown_sync_container_context_with_async_resource() -> None:
    resource_context: ResourceContext[typing.Any] = ResourceContext(is_async=True)
    resource_context.context_stack = AsyncExitStack()
    with pytest.raises(RuntimeError, match="Cannot tear down async context in sync mode"):
        resource_context.sync_tear_down()

@pytest.mark.asyncio
async def test_context_resources_init_and_tear_down() -> None:
    await DIContainer.init_resources()
    await DIContainer.tear_down()

def test_context_resources_wrong_providers_init() -> None:
    with pytest.raises(RuntimeError, match="ContextResource must be generator function"):
        providers.ContextResource(lambda: None)  # type: ignore[arg-type,return-value]

@container_context()
async def test_context_resource_with_dynamic_resource() -> None:
    async with container_context({"resource_type": "sync"}):
        assert (await DIContainer.dynamic_context_resource()).startswith("sync")
    async with container_context({"resource_type": "async_"}):
        assert (await DIContainer.dynamic_context_resource()).startswith("async")
    async with container_context():
        assert (await DIContainer.dynamic_context_resource()).startswith("sync")