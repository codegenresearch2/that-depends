import datetime
import pytest
from tests import container

async def test_batch_providers_overriding() -> None:
    async_resource_mock = datetime.datetime.fromisoformat("2023-01-01")
    sync_resource_mock = datetime.datetime.fromisoformat("2024-01-01")
    async_factory_mock = datetime.datetime.fromisoformat("2025-01-01")
    simple_factory_mock = container.SimpleFactory(dep1="override", dep2=999)
    singleton_mock = container.SingletonFactory(dep1=False)
    obj = object()  # Mock object

    providers_for_overriding = {
        "async_resource": async_resource_mock,
        "sync_resource": sync_resource_mock,
        "simple_factory": simple_factory_mock,
        "singleton": singleton_mock,
        "obj": obj,  # Use consistent naming
    }

    with container.DIContainer.override_providers(providers_for_overriding):
        await container.DIContainer.simple_factory()
        dependent_factory = await container.DIContainer.dependent_factory()
        singleton = await container.DIContainer.singleton()
        obj_instance = await container.DIContainer.obj()  # Resolve the mock object

    assert dependent_factory.simple_factory.dep1 == simple_factory_mock.dep1
    assert dependent_factory.simple_factory.dep2 == simple_factory_mock.dep2
    assert dependent_factory.sync_resource == sync_resource_mock
    assert dependent_factory.async_resource == async_resource_mock
    assert singleton is singleton_mock
    assert obj_instance is obj  # Assert the mock object

    assert (await container.DIContainer.async_resource()) != async_resource_mock


async def test_batch_providers_overriding_sync_resolve() -> None:
    async_resource_mock = datetime.datetime.fromisoformat("2023-01-01")
    sync_resource_mock = datetime.datetime.fromisoformat("2024-01-01")
    simple_factory_mock = container.SimpleFactory(dep1="override", dep2=999)
    singleton_mock = container.SingletonFactory(dep1=False)
    obj = object()  # Mock object

    providers_for_overriding = {
        "async_resource": async_resource_mock,
        "sync_resource": sync_resource_mock,
        "simple_factory": simple_factory_mock,
        "singleton": singleton_mock,
        "obj": obj,  # Use consistent naming
    }

    with container.DIContainer.override_providers(providers_for_overriding):
        container.DIContainer.simple_factory.sync_resolve()
        await container.DIContainer.async_resource.async_resolve()
        dependent_factory = container.DIContainer.dependent_factory.sync_resolve()
        singleton = container.DIContainer.singleton.sync_resolve()
        obj_instance = container.DIContainer.obj.sync_resolve()  # Resolve the mock object

    assert dependent_factory.simple_factory.dep1 == simple_factory_mock.dep1
    assert dependent_factory.simple_factory.dep2 == simple_factory_mock.dep2
    assert dependent_factory.sync_resource == sync_resource_mock
    assert dependent_factory.async_resource == async_resource_mock
    assert singleton is singleton_mock
    assert obj_instance is obj  # Assert the mock object

    assert container.DIContainer.sync_resource.sync_resolve() != sync_resource_mock


def test_providers_overriding_with_context_manager() -> None:
    simple_factory_mock = container.SimpleFactory(dep1="override", dep2=999)

    with container.DIContainer.simple_factory.override_context(simple_factory_mock):
        assert container.DIContainer.simple_factory.sync_resolve() is simple_factory_mock

    assert container.DIContainer.simple_factory.sync_resolve() is not simple_factory_mock


def test_providers_overriding_fail_with_unknown_provider() -> None:
    unknown_provider_name = "unknown_provider_name"
    match = f"Provider with name {unknown_provider_name!r} not found"
    providers_for_overriding = {unknown_provider_name: None}

    with pytest.raises(RuntimeError, match=match), container.DIContainer.override_providers(providers_for_overriding):
        ...  # pragma: no cover


async def test_providers_overriding() -> None:
    async_resource_mock = datetime.datetime.fromisoformat("2023-01-01")
    sync_resource_mock = datetime.datetime.fromisoformat("2024-01-01")
    async_factory_mock = datetime.datetime.fromisoformat("2025-01-01")
    simple_factory_mock = container.SimpleFactory(dep1="override", dep2=999)
    singleton_mock = container.SingletonFactory(dep1=False)
    obj = object()  # Mock object
    container.DIContainer.async_resource.override(async_resource_mock)
    container.DIContainer.sync_resource.override(sync_resource_mock)
    container.DIContainer.simple_factory.override(simple_factory_mock)
    container.DIContainer.singleton.override(singleton_mock)
    container.DIContainer.async_factory.override(async_factory_mock)
    container.DIContainer.obj.override(obj)  # Override the mock object

    await container.DIContainer.simple_factory()
    dependent_factory = await container.DIContainer.dependent_factory()
    singleton = await container.DIContainer.singleton()
    async_factory = await container.DIContainer.async_factory()
    obj_instance = await container.DIContainer.obj()  # Resolve the mock object

    assert dependent_factory.simple_factory.dep1 == simple_factory_mock.dep1
    assert dependent_factory.simple_factory.dep2 == simple_factory_mock.dep2
    assert dependent_factory.sync_resource == sync_resource_mock
    assert dependent_factory.async_resource == async_resource_mock
    assert singleton is singleton_mock
    assert async_factory is async_factory_mock
    assert obj_instance is obj  # Assert the mock object

    container.DIContainer.reset_override()
    assert (await container.DIContainer.async_resource()) != async_resource_mock


async def test_providers_overriding_sync_resolve() -> None:
    async_resource_mock = datetime.datetime.fromisoformat("2023-01-01")
    sync_resource_mock = datetime.datetime.fromisoformat("2024-01-01")
    simple_factory_mock = container.SimpleFactory(dep1="override", dep2=999)
    singleton_mock = container.SingletonFactory(dep1=False)
    obj = object()  # Mock object
    container.DIContainer.async_resource.override(async_resource_mock)
    container.DIContainer.sync_resource.override(sync_resource_mock)
    container.DIContainer.simple_factory.override(simple_factory_mock)
    container.DIContainer.singleton.override(singleton_mock)
    container.DIContainer.obj.override(obj)  # Override the mock object

    container.DIContainer.simple_factory.sync_resolve()
    await container.DIContainer.async_resource.async_resolve()
    dependent_factory = container.DIContainer.dependent_factory.sync_resolve()
    singleton = container.DIContainer.singleton.sync_resolve()
    obj_instance = container.DIContainer.obj.sync_resolve()  # Resolve the mock object

    assert dependent_factory.simple_factory.dep1 == simple_factory_mock.dep1
    assert dependent_factory.simple_factory.dep2 == simple_factory_mock.dep2
    assert dependent_factory.sync_resource == sync_resource_mock
    assert dependent_factory.async_resource == async_resource_mock
    assert singleton is singleton_mock
    assert obj_instance is obj  # Assert the mock object

    container.DIContainer.reset_override()
    assert container.DIContainer.sync_resource.sync_resolve() != sync_resource_mock