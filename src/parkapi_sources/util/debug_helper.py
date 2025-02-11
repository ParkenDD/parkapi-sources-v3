"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from requests import Response

from parkapi_sources.exceptions import MissingConfigException
from parkapi_sources.models import SourceInfo
from parkapi_sources.util import ConfigHelper


class DebugHelper:
    def __init__(self, config_helper: ConfigHelper):
        self.config_helper = config_helper

    def handle_request_response(self, source_info: SourceInfo, response: Response):
        if source_info.uid not in self.config_helper.get('DEBUG_SOURCES', []):
            return

        if not self.config_helper.get('DEBUG_DUMP_DIR'):
            raise MissingConfigException('Config value DEBUG_DUMP_DIR is required for debug dumping')

        debug_dump_dir = Path(self.config_helper.get('DEBUG_DUMP_DIR'), source_info.uid)
        os.makedirs(debug_dump_dir, exist_ok=True)

        metadata_file_path = Path(debug_dump_dir, f'{datetime.now(timezone.utc).isoformat()}-metadata')
        response_body_file_path = Path(debug_dump_dir, f'{datetime.now(timezone.utc).isoformat()}-response-body')

        metadata = [
            f'URL: {response.request.url}',
            f'Method: {response.request.method}',
            f'HTTP Status: {response.status_code}',
            '',
            'Request Headers:',
            *[f'{key}: {value}' for key, value in response.request.headers.items()],
            '',
            'Response Headers:',
            *[f'{key}: {value}' for key, value in response.headers.items()],
            '',
            'Request Body:',
        ]
        if response.request.body:
            metadata.append(str(response.request.body))

        with metadata_file_path.open('w') as metadata_file:
            metadata_file.writelines('\n'.join(metadata))

        with response_body_file_path.open('wb') as response_file:
            for chunk in response.iter_content(chunk_size=128):
                response_file.write(chunk)
