"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, Unpack

from requests import Response, Session

from parkapi_sources.exceptions import MissingConfigException

from .config_helper import ConfigHelper

if TYPE_CHECKING:
    from parkapi_sources.models import SourceInfo


class RequestKwargs(TypedDict):
    url: str | None
    data: NotRequired[Any | None]
    headers: NotRequired[dict[str, str] | None]
    cookies: NotRequired[Any | None]
    files: NotRequired[Any | None]
    auth: NotRequired[Any | None]
    timeout: NotRequired[int | tuple[int, int] | None]
    allow_redirects: NotRequired[bool]
    proxies: NotRequired[Any | None]
    hooks: NotRequired[Any | None]
    stream: NotRequired[Any | None]
    verify: NotRequired[Any | None]
    cert: NotRequired[Any | None]
    json: NotRequired[Any | None]
    params: NotRequired[Any | None]


class RequestHelper:
    config_helper: ConfigHelper

    def __init__(self, config_helper: ConfigHelper):
        self.config_helper = config_helper

    def get(self, *, source_info: 'SourceInfo', **kwargs: Unpack[RequestKwargs]) -> Response:
        return self._request(source_info=source_info, method='get', **kwargs)

    def post(self, *, source_info: 'SourceInfo', **kwargs: Unpack[RequestKwargs]) -> Response:
        return self._request(source_info=source_info, method='post', **kwargs)

    def put(self, *, source_info: 'SourceInfo', **kwargs: Unpack[RequestKwargs]) -> Response:
        return self._request(source_info=source_info, method='put', **kwargs)

    def patch(self, *, source_info: 'SourceInfo', **kwargs: Unpack[RequestKwargs]) -> Response:
        return self._request(source_info=source_info, method='patch', **kwargs)

    def delete(self, *, source_info: 'SourceInfo', **kwargs: Unpack[RequestKwargs]) -> Response:
        return self._request(source_info=source_info, method='delete', **kwargs)

    # Default (connect, read) timeout applied when a caller does not set one. The short connect timeout
    # bounds the TLS handshake, so an unresponsive host cannot block a request indefinitely.
    DEFAULT_TIMEOUT = (5, 30)

    def _request(self, *, source_info: 'SourceInfo', method: str, **kwargs: Unpack[RequestKwargs]) -> Response:
        kwargs.setdefault('timeout', self.DEFAULT_TIMEOUT)

        with Session() as session:
            response = session.request(method=method, **kwargs)

            self._handle_request_response(source_info, response)

            return response

    def _handle_request_response(self, source_info: 'SourceInfo', response: Response) -> None:
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
