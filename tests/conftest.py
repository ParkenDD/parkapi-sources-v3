"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Generator
from unittest.mock import Mock, patch

import pytest

from parkapi_sources.util import ConfigHelper, RequestHelper


@pytest.fixture
def mocked_config_helper() -> Mock:
    config_helper = Mock(ConfigHelper)

    config_helper.get.side_effect = lambda key, default=None: None

    return config_helper


@pytest.fixture
def request_helper(mocked_config_helper: Mock) -> Generator[RequestHelper, None, None]:
    requests_helper = RequestHelper(mocked_config_helper)
    with patch.object(requests_helper, '_handle_request_response', lambda *args, **kwargs: None):
        yield requests_helper
