"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import importlib
import pkgutil
from typing import Type

import parkapi_sources.converters
from parkapi_sources import ParkAPISources
from parkapi_sources.converters import BaseConverter
from parkapi_sources.models import SourceInfo


def _import_all_converter_modules() -> None:
    """
    Import every submodule of parkapi_sources.converters.

    Subclasses only register in ``BaseConverter.__subclasses__()`` once their module has
    been imported. Walking the package guarantees discovery even for converters that are
    not (yet) re-exported from ``converters/__init__.py``.
    """
    package = parkapi_sources.converters
    for module_info in pkgutil.walk_packages(package.__path__, prefix=f'{package.__name__}.'):
        importlib.import_module(module_info.name)


def _all_concrete_converters() -> set[Type[BaseConverter]]:
    """
    Discover every concrete converter class defined in the package.

    A concrete converter is any BaseConverter subclass that sets a real SourceInfo
    instance as its class-level ``source_info`` (the abstract base classes declare it
    as a property instead).
    """
    _import_all_converter_modules()

    def all_subclasses(cls: Type[BaseConverter]):
        for subclass in cls.__subclasses__():
            yield subclass
            yield from all_subclasses(subclass)

    return {
        converter_class
        for converter_class in all_subclasses(BaseConverter)
        if isinstance(getattr(converter_class, 'source_info', None), SourceInfo)
    }


class ParkAPISourcesRegistrationTest:
    def test_all_converters_are_registered_in_converter_classes(self):
        """
        Every concrete converter in the package has to be listed in ParkAPISources.converter_classes.
        """
        registered = set(ParkAPISources.converter_classes)
        discovered = _all_concrete_converters()

        missing = sorted(converter.__name__ for converter in discovered - registered)
        assert not missing, f'Converters missing from ParkAPISources.converter_classes: {missing}'

    def test_converter_classes_have_unique_uids(self):
        uids = [converter_class.source_info.uid for converter_class in ParkAPISources.converter_classes]
        duplicates = sorted({uid for uid in uids if uids.count(uid) > 1})
        assert not duplicates, f'Duplicate converter uids in ParkAPISources.converter_classes: {duplicates}'

    def test_all_converters_are_registered_in_converter_by_uid(self):
        """
        All converters get instantiated and exposed via converter_by_uid keyed by their uid.
        """
        park_api_sources = ParkAPISources(config={'STATIC_GEOJSON_BASE_URL': 'https://example.com'})

        expected_uids = {converter_class.source_info.uid for converter_class in ParkAPISources.converter_classes}

        assert set(park_api_sources.converter_by_uid.keys()) == expected_uids
        assert len(park_api_sources.converter_by_uid) == len(ParkAPISources.converter_classes)

        for uid, converter in park_api_sources.converter_by_uid.items():
            assert isinstance(converter, BaseConverter)
            assert converter.source_info.uid == uid
