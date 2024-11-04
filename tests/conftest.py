"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from parkapi_sources.util import ConfigHelper


@pytest.fixture
def mocked_config_helper() -> Mock:
    return Mock(ConfigHelper)
