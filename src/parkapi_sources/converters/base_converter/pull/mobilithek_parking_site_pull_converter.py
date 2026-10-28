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
    def handle_static_xml_data(
        self,
        static_xml_data: etree.Element,
    ) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        pass

    @abstractmethod
    def handle_realtime_xml_data(
        self,
        realtime_xml_data: etree.Element,
    ) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        pass

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        try:
            static_xml_data = self._get_xml_data(
                subscription_id=self.config_helper.get(
                    f'PARK_API_MOBILITHEK_{self.config_key}_STATIC_SUBSCRIPTION_ID',
                ),
            )
        except etree.XMLSyntaxError as e:
            return [], [self._get_invalid_xml_exception(e)]

        return self.handle_static_xml_data(static_xml_data)

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        # Sources without realtime data have no realtime subscription
        if not self.source_info.has_realtime_data:
            return [], []

        try:
            realtime_xml_data = self._get_xml_data(
                subscription_id=self.config_helper.get(
                    f'PARK_API_MOBILITHEK_{self.config_key}_REALTIME_SUBSCRIPTION_ID',
                ),
            )
        except etree.XMLSyntaxError as e:
            return [], [self._get_invalid_xml_exception(e)]

        return self.handle_realtime_xml_data(realtime_xml_data)

    def _get_invalid_xml_exception(self, error: etree.XMLSyntaxError) -> ImportParkingSiteException:
        return ImportParkingSiteException(
            source_uid=self.source_info.uid,
            message=f'Invalid XML, the publication cannot be parsed: {error}',
        )
