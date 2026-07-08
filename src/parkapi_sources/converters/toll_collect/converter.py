"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from lxml import etree
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import InterUrbanParkingSiteMixin, ParkingRecordStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo

from .models import TollCollectInterUrbanParkingSite, TollCollectParkingRecordStatus


class TollCollectPullConverter(
    InterUrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'TOLL_COLLECT'
    static_validator = DataclassValidator(TollCollectInterUrbanParkingSite)
    realtime_validator = DataclassValidator(TollCollectParkingRecordStatus)

    source_info = SourceInfo(
        uid='toll_collect',
        name='Toll Collect: Truck Parking',
        public_url='https://www.toll-collect.de',
        has_realtime_data=True,
    )

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        # The realtime data does not contain a total capacity, so we fetch the static data as well and calculate the
        # free capacity by subtracting the occupied spaces from the static total capacity.
        static_xml_data = self._get_xml_data(
            subscription_id=self.config_helper.get(f'PARK_API_MOBILITHEK_{self.config_key}_STATIC_SUBSCRIPTION_ID'),
        )
        capacity_by_uid = self._get_capacity_by_uid(static_xml_data)

        realtime_xml_data = self._get_xml_data(
            subscription_id=self.config_helper.get(f'PARK_API_MOBILITHEK_{self.config_key}_REALTIME_SUBSCRIPTION_ID'),
        )

        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        realtime_parking_site_errors: list[ImportParkingSiteException] = []

        realtime_input_dicts: list[dict] = self._transform_realtime_xml_to_realtime_input_dicts(realtime_xml_data)

        for realtime_input_dict in realtime_input_dicts:
            try:
                realtime_item = self.realtime_validator.validate(realtime_input_dict)
                realtime_parking_site_inputs.append(
                    realtime_item.to_realtime_parking_site_input(capacity=capacity_by_uid.get(realtime_item.uid)),
                )

            except ValidationError as e:
                realtime_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=self.get_uid_from_realtime_input_dict(realtime_input_dict),
                        message=str(e.to_dict()),
                    ),
                )

        return realtime_parking_site_inputs, realtime_parking_site_errors

    def _get_capacity_by_uid(self, static_xml_data: etree.Element) -> dict[str, int]:
        capacity_by_uid: dict[str, int] = {}
        for static_input_dict in self._transform_static_xml_to_static_input_dicts(static_xml_data):
            try:
                static_item = self.static_validator.validate(static_input_dict)
            except ValidationError:
                continue
            capacity_by_uid[static_item.id] = static_item.parkingNumberOfSpaces

        return capacity_by_uid
