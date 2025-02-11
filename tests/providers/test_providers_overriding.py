import datetime
import pytest
from tests import container

async def test_overriding_providers() -> None:
    async_resource_mock = datetime.datetime.fromisoformat("2023-01-01")
    sync_resource_mock = datetime.datetime.fromisoformat("2024-01-01")
    async_factory_mock = datetime.datetime.fromisoformat("2025-01-01")
    simple_factory_mock = container.SimpleFactory(dep1="override", dep2=999)
    singleton_mock = container.SingletonFactory(dep1=False)
    object_mock = object()  # Adding the missing mock object

    providers_for_overriding = {
        "async_resource": async_resource_mock,
        "sync_resource": sync_resource_mock,
        "simple_factory": simple_factory_mock,
        "singleton": singleton_mock,
        "async_factory": async_factory_mock,
        "object": object_mock,  # Including the missing mock object
    }

    with container.DIContainer.override_providers(providers_for_overriding):
        await container.DIContainer.simple_factory()
        dependent_factory = await container.DIContainer.dependent_factory()
        singleton = await container.DIContainer.singleton()
        async_factory = await container.DIContainer.async_factory()
        obj = await container.DIContainer.object()  # Awaiting the new mock object

    assert dependent_factory.simple_factory.dep1 == simple_factory_mock.dep1
    assert dependent_factory.simple_factory.dep2 == simple_factory_mock.dep2
    assert dependent_factory.sync_resource == sync_resource_mock
    assert dependent_factory.async_resource == async_resource_mock
    assert singleton is singleton_mock
    assert async_factory is async_factory_mock
    assert obj is not None  # Ensuring the mock object is not None

    container.DIContainer.reset_override()
    assert container.DIContainer.sync_resource.sync_resolve() != sync_resource_mock