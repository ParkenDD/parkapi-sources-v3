"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from lxml import etree

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.util import XMLHelper

from .pull_converter import PullConverter


class MobilithekPullConverter(PullConverter, ABC):
    xml_helper = XMLHelper()

    @property
    @abstractmethod
    def config_key(self) -> str:
        pass

    @abstractmethod
    def _handle_static_xml_data(
        self,
        static_xml_data: etree.Element,
    ) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        pass

    @abstractmethod
    def _handle_realtime_xml_data(
        self,
        realtime_xml_data: etree.Element,
    ) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_config_keys = [
            'PARK_API_MOBILITHEK_CERT',
            'PARK_API_MOBILITHEK_KEY',
            f'PARK_API_MOBILITHEK_{self.config_key}_STATIC_SUBSCRIPTION_ID',
            f'PARK_API_MOBILITHEK_{self.config_key}_REALTIME_SUBSCRIPTION_ID',
        ]

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_xml_data = self._get_xml_data(
            subscription_id=self.config_helper.get(f'PARK_API_MOBILITHEK_{self.config_key}_STATIC_SUBSCRIPTION_ID'),
        )

        return self._handle_static_xml_data(static_xml_data)

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_xml_data = self._get_xml_data(
            subscription_id=self.config_helper.get(f'PARK_API_MOBILITHEK_{self.config_key}_REALTIME_SUBSCRIPTION_ID'),
        )

        return self._handle_realtime_xml_data(realtime_xml_data)

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

        root = etree.fromstring(response.text, parser=etree.XMLParser(resolve_entities=False))  # noqa: S320

        return root
