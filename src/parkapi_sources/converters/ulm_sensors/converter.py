"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import (
    ParkingSitePullConverter,
    ParkingSpotPullConverter,
    StaticGeojsonDataMixin,
)
from parkapi_sources.exceptions import ImportParkingSiteException, ImportParkingSpotException
from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    RealtimeParkingSpotInput,
    SourceInfo,
    StaticParkingSiteInput,
    StaticParkingSpotInput,
)

from .validators import UlmSensorsParkingSiteInput, UlmSensorsParkingSpotInput


class UlmSensorsPullConverter(ParkingSpotPullConverter, ParkingSitePullConverter, StaticGeojsonDataMixin):
    required_config_keys = [
        'PARK_API_ULM_SENSORS_IDS',
        'PARK_API_ULM_SENSORS_CLIENT_ID',
        'PARK_API_ULM_SENSORS_USER',
        'PARK_API_ULM_SENSORS_PASSWORD',
    ]
    ulm_sensors_parking_sites_validator = DataclassValidator(UlmSensorsParkingSiteInput)
    ulm_sensors_parking_spots_validator = DataclassValidator(UlmSensorsParkingSpotInput)

    source_info = SourceInfo(
        uid='ulm_sensors',
        name='Stadt Ulm: E-Quartiershubs Sensors',
        timezone='Europe/Berlin',
        source_url='https://citysens-iot.swu.de',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_static_parking_site_inputs_and_exceptions(
            source_uid=self.source_info.uid,
        )

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        realtime_ulm_sensors_inputs, import_parking_site_exceptions = self._get_raw_realtime_parking_sites()

        for realtime_ulm_sensors_input in realtime_ulm_sensors_inputs:
            realtime_parking_site_inputs.append(realtime_ulm_sensors_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _get_raw_realtime_parking_sites(
        self,
    ) -> tuple[list[UlmSensorsParkingSiteInput], list[ImportParkingSiteException]]:
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
        return self._get_static_parking_spots_inputs_and_exceptions(
            source_uid=self.source_info.uid,
        )

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        realtime_parking_spot_inputs: list[RealtimeParkingSpotInput] = []

        realtime_ulm_sensors_inputs, realtime_parking_spot_errors = self._get_raw_realtime_parking_spots()

        for realtime_ulm_sensors_input in realtime_ulm_sensors_inputs:
            realtime_parking_spot_inputs.append(realtime_ulm_sensors_input.to_realtime_parking_spot_input())

        return realtime_parking_spot_inputs, realtime_parking_spot_errors

    def _get_raw_realtime_parking_spots(
        self,
    ) -> tuple[list[UlmSensorsParkingSpotInput], list[ImportParkingSpotException]]:
        realtime_ulm_sensors_inputs: list[UlmSensorsParkingSpotInput] = []
        import_parking_spot_exceptions: list[ImportParkingSpotException] = []

        parking_spot_dicts: list[dict] = []
        sensor_ids = self.config_helper.get('PARK_API_ULM_SENSORS_IDS').split(',')

        for sensor_id in sensor_ids:
            response = self.request_get(
                url=f'{self.source_info.source_url}/consumer-api/v1/collections/sensors/{sensor_id}/data?count=1',
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
            data={
                'client_id': self.config_helper.get('PARK_API_ULM_SENSORS_CLIENT_ID'),
                'grant_type': 'password',
                'username': self.config_helper.get('PARK_API_ULM_SENSORS_USER'),
                'password': self.config_helper.get('PARK_API_ULM_SENSORS_PASSWORD'),
            },
            timeout=30,
        )
        token_data = response.json()
        return token_data['access_token']
