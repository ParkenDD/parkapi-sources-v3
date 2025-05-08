"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from lxml import etree

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.util import XMLHelper

from .mobilithek_pull_converter import MobilithekPullConverterMixin
from .pull_converter import ParkingSitePullConverter


class MobilithekParkingSitePullConverter(MobilithekPullConverterMixin, ParkingSitePullConverter, ABC):
    xml_helper = XMLHelper()

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
