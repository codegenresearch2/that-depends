import datetime
import pytest
from tests import container

def test_batch_providers_overriding() -> None:
    async_resource_mock = datetime.datetime.fromisoformat("2023-01-01")
    sync_resource_mock = datetime.datetime.fromisoformat("2024-01-01")
    async_factory_mock = datetime.datetime.fromisoformat("2025-01-01")
    simple_factory_mock = container.SimpleFactory(dep1="override", dep2=999)
    singleton_mock = container.SingletonFactory(dep1=False)

    providers_for_overriding = {
        "async_resource": async_resource_mock,
        "sync_resource": sync_resource_mock,
        "simple_factory": simple_factory_mock,
        "singleton": singleton_mock,
        "object": None,  # Use "object" instead of "object_mock"
    }

    with container.DIContainer.override_providers(providers_for_overriding):
        await container.DIContainer.simple_factory()
        dependent_factory = await container.DIContainer.dependent_factory()
        singleton = await container.DIContainer.singleton()
        obj = await container.DIContainer.object()  # Use "object" instead of "object_mock"

    assert dependent_factory.simple_factory.dep1 == simple_factory_mock.dep1
    assert dependent_factory.simple_factory.dep2 == simple_factory_mock.dep2
    assert dependent_factory.sync_resource == sync_resource_mock
    assert dependent_factory.async_resource == async_resource_mock
    assert singleton is singleton_mock
    assert obj is None  # Ensure the mock object is correctly asserted

    assert (await container.DIContainer.async_resource()) != async_resource_mock

def test_batch_providers_overriding_sync_resolve() -> None:
    async_resource_mock = datetime.datetime.fromisoformat("2023-01-01")
    sync_resource_mock = datetime.datetime.fromisoformat("2024-01-01")
    simple_factory_mock = container.SimpleFactory(dep1="override", dep2=999)
    singleton_mock = container.SingletonFactory(dep1=False)

    providers_for_overriding = {
        "async_resource": async_resource_mock,
        "sync_resource": sync_resource_mock,
        "simple_factory": simple_factory_mock,
        "singleton": singleton_mock,
        "object": None,  # Use "object" instead of "object_mock"
    }

    with container.DIContainer.override_providers(providers_for_overriding):
        container.DIContainer.simple_factory.sync_resolve()
        await container.DIContainer.async_resource.async_resolve()
        dependent_factory = container.DIContainer.dependent_factory.sync_resolve()
        singleton = container.DIContainer.singleton.sync_resolve()
        obj = container.DIContainer.object.sync_resolve()  # Use "object" instead of "object_mock"

    assert dependent_factory.simple_factory.dep1 == simple_factory_mock.dep1
    assert dependent_factory.simple_factory.dep2 == simple_factory_mock.dep2
    assert dependent_factory.sync_resource == sync_resource_mock
    assert dependent_factory.async_resource == async_resource_mock
    assert singleton is singleton_mock
    assert obj is None  # Ensure the mock object is correctly asserted

    assert container.DIContainer.sync_resource.sync_resolve() != sync_resource_mock