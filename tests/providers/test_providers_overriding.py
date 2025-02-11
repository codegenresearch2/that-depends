import datetime
import pytest
from tests import container

async def test_providers_overriding_sync_resolve() -> None:
    async_resource_mock = datetime.datetime.fromisoformat("2023-01-01")
    sync_resource_mock = datetime.datetime.fromisoformat("2024-01-01")
    simple_factory_mock = container.SimpleFactory(dep1="override", dep2=999)
    singleton_mock = container.SingletonFactory(dep1=False)
    async_factory_mock = datetime.datetime.fromisoformat("2025-01-01")

    providers_for_overriding = {
        "async_resource": async_resource_mock,
        "sync_resource": sync_resource_mock,
        "simple_factory": simple_factory_mock,
        "singleton": singleton_mock,
        "async_factory": async_factory_mock,
    }

    with container.DIContainer.override_providers(providers_for_overriding):
        container.DIContainer.simple_factory.sync_resolve()
        await container.DIContainer.async_resource.async_resolve()
        dependent_factory = container.DIContainer.dependent_factory.sync_resolve()
        singleton = container.DIContainer.singleton.sync_resolve()
        async_factory = await container.DIContainer.async_factory()

    assert dependent_factory.simple_factory.dep1 == simple_factory_mock.dep1
    assert dependent_factory.simple_factory.dep2 == simple_factory_mock.dep2
    assert dependent_factory.sync_resource == sync_resource_mock
    assert dependent_factory.async_resource == async_resource_mock
    assert singleton is singleton_mock
    assert async_factory is async_factory_mock

    container.DIContainer.reset_override()
    assert container.DIContainer.sync_resource.sync_resolve() != sync_resource_mock