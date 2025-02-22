"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import shutil
from pathlib import Path

import pytest
import requests

from parkapi_sources.exceptions import MissingConfigException
from parkapi_sources.models import SourceInfo
from parkapi_sources.util import ConfigHelper, RequestHelper


@pytest.fixture
def source_info() -> SourceInfo:
    return SourceInfo(
        uid='test-source',
        name='Test Source',
        has_realtime_data=False,
    )


@pytest.fixture
def dump_dir() -> Path:
    dump_dir = Path(Path(__file__).parent.parent.parent, 'temp')
    if dump_dir.exists():
        shutil.rmtree(dump_dir)
    return dump_dir


class RequestHelperTest:
    @staticmethod
    def test_handle_request_response(dump_dir: Path, source_info: SourceInfo):
        request_helper = RequestHelper(
            config_helper=ConfigHelper(
                {
                    'DEBUG_SOURCES': ['test-source'],
                    'DEBUG_DUMP_DIR': str(dump_dir),
                },
            ),
        )

        response = requests.get(
            'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/refs/heads/main/sources/freiburg.geojson',
            timeout=30,
        )

        request_helper._handle_request_response(source_info, response)

        assert dump_dir.exists()

        sub_dump_dir = Path(dump_dir, 'test-source')
        assert sub_dump_dir.exists()
        files = list(sub_dump_dir.glob('*'))
        assert len(files) == 2
        assert len([file for file in files if str(file).endswith('-metadata')]) == 1
        assert len([file for file in files if str(file).endswith('-response-body')]) == 1

    @staticmethod
    def test_handle_request_response_not_in_debug(dump_dir: Path, source_info: SourceInfo):
        request_helper = RequestHelper(
            config_helper=ConfigHelper(
                {
                    'DEBUG_SOURCES': ['other-source'],
                    'DEBUG_DUMP_DIR': str(dump_dir),
                },
            ),
        )

        response = requests.get(
            'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/refs/heads/main/sources/freiburg.geojson',
            timeout=30,
        )

        request_helper._handle_request_response(source_info, response)

        assert not dump_dir.exists()

    @staticmethod
    def test_handle_request_response_dir_not_set(dump_dir: Path, source_info: SourceInfo):
        request_helper = RequestHelper(
            config_helper=ConfigHelper(
                {
                    'DEBUG_SOURCES': ['test-source'],
                },
            ),
        )

        response = requests.get(
            'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/refs/heads/main/sources/freiburg.geojson',
            timeout=30,
        )

        with pytest.raises(MissingConfigException):
            request_helper._handle_request_response(source_info, response)
