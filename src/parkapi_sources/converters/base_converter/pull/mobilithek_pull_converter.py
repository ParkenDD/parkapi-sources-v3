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
    # The Mobilithek offers DATEX II v2 and v3 publications at different endpoints
    mobilithek_datex2_version: int = 2
    # Publications in the Mobilithek container format wrap the actual document and have an endpoint of their own
    mobilithek_container: bool = False

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
        if self.mobilithek_container:
            url = f'https://mobilithek.info:8443/mobilithek/api/v1.0/container/subscription?subscriptionID={subscription_id}'
        elif self.mobilithek_datex2_version == 3:
            url = f'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/datexv3?subscriptionID={subscription_id}'
        else:
            url = (
                f'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/{subscription_id}'
                f'/clientPullService?subscriptionID={subscription_id}'
            )
        # Create an isolated session, because cert is set globally otherwise
        response = self.request_get(
            url=url,
            cert=(
                self.config_helper.get('PARK_API_MOBILITHEK_CERT'),
                self.config_helper.get('PARK_API_MOBILITHEK_KEY'),
            ),
        )
        # Parse the raw bytes: lxml uses the encoding of the XML declaration, or UTF-8 if there is none. Parsing
        # response.text fails at documents with an encoding declaration, and python requests would assume ISO-8859-1
        # because of RFC 2616.
        root = etree.fromstring(response.content, parser=etree.XMLParser(resolve_entities=False))  # noqa: S320

        if self.mobilithek_container:
            return self._unwrap_container(root)

        return root

    @staticmethod
    def _unwrap_container(root: etree.Element) -> etree.Element:
        """
        The container format has the actual document as single child of container/body/xml. If the container does not
        look like this, the container itself is returned, so the following import fails at the unexpected root element.
        """
        xml_element = root.find('{*}body/{*}xml')
        if xml_element is None:
            return root
        children = [child for child in xml_element if isinstance(child.tag, str)]
        if len(children) != 1:
            return root
        return children[0]
