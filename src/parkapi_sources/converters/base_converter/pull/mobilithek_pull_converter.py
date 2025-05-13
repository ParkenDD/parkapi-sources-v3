"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from typing import Callable

from lxml import etree

from parkapi_sources.util import ConfigHelper, XMLHelper


class MobilithekPullConverterMixin(ABC):
    xml_helper = XMLHelper()
    config_helper: ConfigHelper
    request_get: Callable

    @property
    @abstractmethod
    def config_key(self) -> str:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_config_keys = [
            'PARK_API_MOBILITHEK_CERT',
            'PARK_API_MOBILITHEK_KEY',
            f'PARK_API_MOBILITHEK_{self.config_key}_STATIC_SUBSCRIPTION_ID',
            f'PARK_API_MOBILITHEK_{self.config_key}_REALTIME_SUBSCRIPTION_ID',
        ]

    def _get_xml_data(self, subscription_id: int) -> etree.Element:
        url = (
            f'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/{subscription_id}'
            f'/clientPullService?subscriptionID={subscription_id}'
        )
        # Create an isolated session, because cert is set globally otherwise
        response = self.request_get(
            url=url,
            timeout=30,
            cert=(
                self.config_helper.get('PARK_API_MOBILITHEK_CERT'),
                self.config_helper.get('PARK_API_MOBILITHEK_KEY'),
            ),
        )
        # Force UTF-8 encoding, because python requests sets ISO-8859-1 because of RFC 2616
        response.encoding = 'utf-8'

        root = etree.fromstring(response.text, parser=etree.XMLParser(resolve_entities=False))  # noqa: S320

        return root
