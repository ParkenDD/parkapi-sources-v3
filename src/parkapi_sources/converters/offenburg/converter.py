"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from lxml import etree

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingRecordStatusMixin, UrbanParkingSiteMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo


class OffenburgPullConverter(
    UrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    Some parking sites have no number of spaces. They are ignored per default, which can be disabled with the config
    key PARK_API_OFFENBURG_IGNORE_MISSING_CAPACITIES.
    """

    config_key = 'OFFENBURG'

    source_info = SourceInfo(
        uid='offenburg',
        name='Technische Betriebe Offenburg',
        public_url='https://mobilithek.info/offers/978250862019141632',
        attribution_contributor='Technische Betriebe Offenburg',
        has_realtime_data=True,
    )

    def _should_ignore_dataset(self, static_input_dict: dict) -> bool:
        if self.config_helper.get('PARK_API_OFFENBURG_IGNORE_MISSING_CAPACITIES', True):
            return static_input_dict.get('parkingNumberOfSpaces') is None

        return False

    def _transform_static_xml_to_static_input_dicts(self, xml_data: etree.Element) -> list[dict]:
        return [
            static_input_dict
            for static_input_dict in super()._transform_static_xml_to_static_input_dicts(xml_data)
            if not self._should_ignore_dataset(static_input_dict)
        ]

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs, realtime_parking_site_errors = super().get_realtime_parking_sites()

        if not self.config_helper.get('PARK_API_OFFENBURG_IGNORE_MISSING_CAPACITIES', True):
            return realtime_parking_site_inputs, realtime_parking_site_errors

        # Parking sites the static import ignores do not exist, so we fetch the static data to skip them here as well
        static_xml_data = self._get_xml_data(
            subscription_id=self.config_helper.get(f'PARK_API_MOBILITHEK_{self.config_key}_STATIC_SUBSCRIPTION_ID'),
        )
        ignored_uids: set[str] = {
            static_input_dict.get('id')
            for static_input_dict in super()._transform_static_xml_to_static_input_dicts(static_xml_data)
            if self._should_ignore_dataset(static_input_dict)
        }

        return [
            realtime_parking_site_input
            for realtime_parking_site_input in realtime_parking_site_inputs
            if realtime_parking_site_input.uid not in ignored_uids
        ], realtime_parking_site_errors
