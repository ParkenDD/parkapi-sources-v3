"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSpotPullConverter, ParkingSitePullConverter, StaticGeojsonDataMixin
from parkapi_sources.exceptions import ImportParkingSpotException, ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSpotInput, SourceInfo, StaticParkingSpotInput, GeojsonInput, StaticParkingSiteInput, RealtimeParkingSiteInput

from .validators import UlmSensorsParkingSiteInput, UlmSensorsParkingSpotInput


class UlmSensorsPullConverter(ParkingSpotPullConverter, ParkingSitePullConverter, StaticGeojsonDataMixin):
    config_prefix = 'ULM_SENSORS'
    ulm_sensors_parking_sites_validator = DataclassValidator(UlmSensorsParkingSiteInput)
    ulm_sensors_parking_spots_validator = DataclassValidator(UlmSensorsParkingSpotInput)

    source_info = SourceInfo(
        uid='ulm_sensors',
        name='Stadt Ulm: E-Quartiershubs Sensors',
        timezone='Europe/Berlin',
        source_url='https://citysens-iot.swu.de'
        has_realtime_data=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_config_keys = [
            f'PARK_API_{self.config_prefix}_USER',
            f'PARK_API_{self.config_prefix}_PASSWORD',
            f'PARK_API_{self.config_prefix}_CLIENT_ID',
            f'PARK_API_{self.config_prefix}_ENDPOINT_IDS',
        ]

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs, import_parking_site_exceptions = (
            self._get_static_parking_site_inputs_and_exceptions(
                source_uid=self.source_info.uid,
            )
        )

        return static_parking_site_inputs, import_parking_site_exceptions
    
    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        realtime_ulm_sensors_inputs, import_parking_site_exceptions = self._get_raw_realtime_parking_sites()

        for realtime_ulm_sensors_input in realtime_ulm_sensors_inputs:
            realtime_parking_site_inputs.append(realtime_ulm_sensors_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions
    
    def _get_raw_realtime_parking_sites(self) -> tuple[list[UlmSensorsParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_ulm_sensors_inputs: list[UlmSensorsParkingSiteInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(
            url=f'{self.source_info.source_url}/consumer-api/v1/collections/sensors/pbg_all_carparks/data',
            headers={'Authorization': f'Bearer {self._request_token()}'},
            timeout=60,
        )
        parking_site_dicts = response.json()
        
        for parking_site_dict in parking_site_dicts:
            try:
                realtime_ulm_sensors_inputs.append(self.ulm_sensors_parking_sites_validator.validate(parking_site_dict))
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('uid'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )
        
        return realtime_ulm_sensors_inputs, import_parking_site_exceptions
    

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs, static_parking_spot_errors = (
            self._get_static_parking_site_inputs_and_exceptions(
                source_uid=self.source_info.uid,
            )
        )

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

        return static_parking_spot_inputs, static_parking_spot_errors

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        realtime_parking_spot_inputs: list[RealtimeParkingSpotInput] = []

        realtime_ulm_sensors_inputs, realtime_parking_spot_errors = self._get_raw_realtime_parking_spots()

        for realtime_ulm_sensors_input in realtime_ulm_sensors_inputs:
            realtime_parking_spot_inputs.append(realtime_ulm_sensors_input.to_realtime_parking_spot_input())

        return realtime_parking_spot_inputs, realtime_parking_spot_errors
    
    def _get_raw_realtime_parking_spots(self) -> tuple[list[UlmSensorsParkingSpotInput], list[ImportParkingSpotException]]:
        realtime_ulm_sensors_inputs: list[UlmSensorsParkingSpotInput] = []
        import_parking_spot_exceptions: list[ImportParkingSpotException] = []

        parking_spot_dicts: list[dict] = []
        endpoint_ids = self.config_helper.get(f'PARK_API_{self.config_prefix}_ENDPOINT_IDS').split(',')

        for endpoint_id in endpoint_ids:
            response = self.request_get(
                url=f'{self.source_info.source_url}/consumer-api/v1/collections/sensors/{endpoint_id}/data?count=1',
                headers={'Authorization': f'Bearer {self._request_token()}'},
                timeout=60,
            )
        parking_spot_dicts += response.json()

        for parking_spot_dict in parking_spot_dicts:
            try:
                realtime_ulm_sensors_inputs.append(self.ulm_sensors_parking_spots_validator.validate(parking_spot_dict))
            except ValidationError as e:
                import_parking_spot_exceptions.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=parking_spot_dict.get('uid'),
                        message=f'validation error for {parking_spot_dict}: {e.to_dict()}',
                    ),
                )
        
        return realtime_ulm_sensors_inputs, import_parking_spot_exceptions
    
    def _request_token(self) -> str:
        response = self.request_post(
            url=f'{self.source_info.source_url}/auth/realms/ocon/protocol/openid-connect/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            json={
                'client_id': self.config_helper.get(f'PARK_API_{self.config_prefix}_CLIENT_ID'),
                'grant_type': 'password',
                'username': self.config_helper.get(f'PARK_API_{self.config_prefix}_USER'),
                'password': self.config_helper.get(f'PARK_API_{self.config_prefix}_PASSWORD'),
            },
            timeout=30,
        )
        return response.content
