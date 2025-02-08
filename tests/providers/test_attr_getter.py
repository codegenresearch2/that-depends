import random
from dataclasses import dataclass, field
import pytest
from typing import Any

from that_depends import providers
from that_depends.providers.attr_getter import _get_value_from_object_by_dotted_path


@dataclass
class Nested2:
    some_const = 144


@dataclass
class Nested1:
    nested2_attr: Nested2 = field(default_factory=Nested2)


@dataclass
class Settings:
    some_str_value: str = 'some_string_value'
    some_int_value: int = 3453621
    nested1_attr: Nested1 = field(default_factory=Nested1)


@dataclass
class NestingTestDTO: ...


@pytest.fixture(params=[providers.Singleton, providers.Factory, providers.AsyncFactory])
def settings_provider(request):
    if request.param == providers.Singleton:
        return providers.Singleton(Settings)
    elif request.param == providers.Factory:
        return providers.Factory(Settings)
    elif request.param == providers.AsyncFactory:
        return providers.AsyncFactory(Settings)


@pytest.mark.asyncio
async def test_async_attr_getter_with_zero_attribute_depth(settings_provider):
    attr_getter = settings_provider.some_str_value
    assert attr_getter.sync_resolve() == Settings().some_str_value


@pytest.mark.asyncio
async def test_async_attr_getter_with_more_than_zero_attribute_depth(settings_provider):
    attr_getter = settings_provider.nested1_attr.nested2_attr.some_const
    assert attr_getter.sync_resolve() == Nested2().some_const


@pytest.mark.parametrize(
    ('field_count', 'test_field_name', 'test_value'), [
        (1, 'test_field', 'sdf6fF^SF(FF*4ffsf'),
        (5, 'nested_field', -252625),
        (50, '50_lvl_field', 909234235)
    ]
)
def test_sync_nesting_levels(field_count: int, test_field_name: str, test_value: str | int):
    obj = NestingTestDTO()
    fields = [f'field_{i}' for i in range(1, field_count + 1)]
    random.shuffle(fields)

    attr_path = '.'.join(fields) + f'.{test_field_name}'
    obj_copy = obj

    while fields:
        field_name = fields.pop(0)
        setattr(obj_copy, field_name, NestingTestDTO())
        obj_copy = obj_copy.__getattribute__(field_name)

    setattr(obj_copy, test_field_name, test_value)

    attr_value = _get_value_from_object_by_dotted_path(obj, attr_path)
    assert attr_value == test_value


def test_attr_getter_with_invalid_attribute(settings_provider):
    with pytest.raises(AttributeError):
        settings_provider.nested1_attr.nested2_attr.__some_private__  # noqa: B018
    with pytest.raises(AttributeError):
        settings_provider.nested1_attr.__another_private__  # noqa: B018
    with pytest.raises(AttributeError):
        settings_provider.nested1_attr._final_private_  # noqa: B018
