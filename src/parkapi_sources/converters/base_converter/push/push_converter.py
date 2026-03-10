"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from parkapi_sources.converters import BaseConverter
from parkapi_sources.converters.base_converter.pull.static_patch_mixin import StaticPatchMixin


class PushConverter(StaticPatchMixin, BaseConverter, ABC):
    pass
