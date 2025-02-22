"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import os
import ssl
from datetime import datetime, timezone
from pathlib import Path

from requests import Response, Session
from requests.adapters import HTTPAdapter
from requests.utils import DEFAULT_CA_BUNDLE_PATH, extract_zipped_paths
from urllib3.util import create_urllib3_context

from parkapi_sources.exceptions import MissingConfigException
from parkapi_sources.models import SourceInfo
from parkapi_sources.util import ConfigHelper


class CustomHTTPAdapter(HTTPAdapter):
    """
    This class is necessary because of https://github.com/psf/requests/issues/6726#issuecomment-2660565040
    and should be removed after requests resolved this bug.
    """

    @staticmethod
    def _get_reset_ssl_context() -> ssl.SSLContext:
        # Create a fresh SSLContext and load CA certificates
        ssl_context = create_urllib3_context()
        ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))
        return ssl_context

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self._get_reset_ssl_context()
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self._get_reset_ssl_context()
        return super().proxy_manager_for(*args, **kwargs)


class RequestHelper:
    def __init__(self, config_helper: ConfigHelper):
        self.config_helper = config_helper

    def get(self, *, source_info: SourceInfo, **kwargs) -> Response:
        return self._request(source_info=source_info, method='get', **kwargs)

    def post(self, *, source_info: SourceInfo, **kwargs) -> Response:
        return self._request(source_info=source_info, method='post', **kwargs)

    def put(self, *, source_info: SourceInfo, **kwargs) -> Response:
        return self._request(source_info=source_info, method='put', **kwargs)

    def patch(self, *, source_info: SourceInfo, **kwargs) -> Response:
        return self._request(source_info=source_info, method='patch', **kwargs)

    def delete(self, *, source_info: SourceInfo, **kwargs) -> Response:
        return self._request(source_info=source_info, method='delete', **kwargs)

    def _request(self, *, source_info: SourceInfo, method: str, **kwargs) -> Response:
        with Session() as session:
            # Can be removed after https://github.com/psf/requests/issues/6726#issuecomment-2660565040 is resolved
            session.mount('https://', CustomHTTPAdapter())

            response = session.request(method=method, **kwargs)

            self._handle_request_response(source_info, response)

            return response

    def _handle_request_response(self, source_info: SourceInfo, response: Response):
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
