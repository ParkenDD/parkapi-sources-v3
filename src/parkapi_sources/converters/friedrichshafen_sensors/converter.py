"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.datex2 import ParkingRecordStatusMixin, UrbanParkingSiteMixin
from parkapi_sources.converters.base_converter.pull import MobilithekPullConverterMixin, ParkingSpotPullConverter
from parkapi_sources.exceptions import ImportParkingSpotException
from parkapi_sources.models import RealtimeParkingSpotInput, SourceInfo, StaticParkingSpotInput

from .validators import FriedrichshafenSensorsParkingRecordStatus, FriedrichshafenSensorsParkingSpot


class FriedrichshafenSensorsPullConverter(
    UrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekPullConverterMixin,
    ParkingSpotPullConverter,
):
    config_key = 'FRIEDRICHSHAFEN_SENSORS'
    static_validator = DataclassValidator(FriedrichshafenSensorsParkingSpot)
    realtime_validator = DataclassValidator(FriedrichshafenSensorsParkingRecordStatus)

    source_info = SourceInfo(
        uid='friedrichshafen_sensors',
        name='Stadt Friedrichshafen: Sensors',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_xml_data = self._get_xml_data(
            subscription_id=self.config_helper.get(f'PARK_API_MOBILITHEK_{self.config_key}_STATIC_SUBSCRIPTION_ID'),
        )

        static_parking_spot_inputs: list[StaticParkingSpotInput] = []
        static_parking_spot_errors: list[ImportParkingSpotException] = []

        static_input_dicts: list[dict] = self._transform_static_xml_to_static_input_dicts(static_xml_data)

        for static_input_dict in static_input_dicts:
            try:
                static_item = self.static_validator.validate(static_input_dict)
                static_parking_spot_input = static_item.to_static_parking_spot_input()

                static_parking_spot_inputs.append(static_parking_spot_input)

            except ValidationError as e:
                static_parking_spot_errors.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=self.get_uid_from_static_input_dict(static_input_dict),
                        message=str(e.to_dict()),
                        data=static_input_dict,
                    ),
                )

        return self.apply_static_patches(static_parking_spot_inputs), static_parking_spot_errors

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        realtime_xml_data = self._get_xml_data(
            subscription_id=self.config_helper.get(f'PARK_API_MOBILITHEK_{self.config_key}_REALTIME_SUBSCRIPTION_ID'),
        )
        realtime_parking_spot_inputs: list[RealtimeParkingSpotInput] = []
        realtime_parking_spot_errors: list[ImportParkingSpotException] = []

        realtime_input_dicts: list[dict] = self._transform_realtime_xml_to_realtime_input_dicts(realtime_xml_data)

        for realtime_input_dict in realtime_input_dicts:
            try:
                realtime_item = self.realtime_validator.validate(realtime_input_dict)
                realtime_parking_spot_inputs.append(realtime_item.to_realtime_parking_spot_input())

            except ValidationError as e:
                realtime_parking_spot_errors.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=self.get_uid_from_realtime_input_dict(realtime_input_dict),
                        message=str(e.to_dict()),
                        data=realtime_input_dicts,
                    ),
                )

        return realtime_parking_spot_inputs, realtime_parking_spot_errors
