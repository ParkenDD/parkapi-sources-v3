"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter, ParkingSpotPullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportParkingSpotException
from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    RealtimeParkingSpotInput,
    SourceInfo,
    StaticParkingSiteInput,
    StaticParkingSpotInput,
)

from .validators import (
    PMSensadeParkingLot,
    PMSensadeParkingLotInput,
    PMSensadeParkingLotParkingSpace,
    PMSensadeParkingLotsInput,
    PMSensadeParkingLotStatus,
)


class PMSensadePullConverter(ParkingSitePullConverter, ParkingSpotPullConverter):
    required_config_keys = [
        'PARK_API_P_M_SENSADE_EMAIL',
        'PARK_API_P_M_SENSADE_PASSWORD',
    ]

    p_m_sensade_parking_lot_input_validator = DataclassValidator(PMSensadeParkingLotInput)
    p_m_sensade_parking_lots_input_validator = DataclassValidator(PMSensadeParkingLotsInput)
    p_m_sensade_parking_lot_status_validator = DataclassValidator(PMSensadeParkingLotStatus)
    p_m_sensade_parking_lot_validator = DataclassValidator(PMSensadeParkingLot)
    p_m_sensade_parking_lot_parking_space_validator = DataclassValidator(PMSensadeParkingLotParkingSpace)

    source_info = SourceInfo(
        uid='p_m_sensade',
        name='Sensade Parking Lots',
        timezone='Europe/Berlin',
        public_url='https://api.sensade.com/docs/index.html?urls.primaryName=ParkingLotManager',
        source_url='https://api.sensade.com',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        static_p_m_sensade_inputs, import_parking_site_exceptions = self._get_raw_static_parking_sites()

        for static_p_m_sensade_input in static_p_m_sensade_inputs:
            static_parking_site_inputs.append(static_p_m_sensade_input.to_static_parking_site_input())

        return static_parking_site_inputs, import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        realtime_p_m_sensade_inputs, import_parking_site_exceptions = self._get_raw_realtime_parking_sites()

        for realtime_p_m_sensade_input in realtime_p_m_sensade_inputs:
            realtime_parking_site_inputs.append(realtime_p_m_sensade_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[StaticParkingSpotInput] = []
        static_p_m_sensade_inputs, import_parking_spot_exceptions = self._get_raw_static_parking_spots()

        for static_p_m_sensade_input in static_p_m_sensade_inputs:
            static_parking_spot_inputs.append(static_p_m_sensade_input.to_static_parking_spot_input())

        return static_parking_spot_inputs, import_parking_spot_exceptions

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        return [], []

    def _get_raw_static_parking_spots(
        self,
    ) -> tuple[list[PMSensadeParkingLotParkingSpace], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[PMSensadeParkingLotParkingSpace] = []
        import_parking_spot_exceptions: list[ImportParkingSpotException] = []

        static_p_m_sensade_inputs, import_parking_site_exceptions = self._get_raw_static_parking_sites()
        parking_spot_dicts: list[dict] = []

        for static_p_m_sensade_input in static_p_m_sensade_inputs:
            static_parking_site_input = static_p_m_sensade_input.to_static_parking_site_input()
            for parking_space in static_p_m_sensade_input.parkingSpaces:
                parking_space['name'] = static_parking_site_input.name
                parking_space['address'] = static_parking_site_input.address
                parking_space['static_data_updated_at'] = static_parking_site_input.static_data_updated_at.isoformat()
                parking_space['purpose'] = static_parking_site_input.purpose.value
                parking_space['type'] = static_parking_site_input.type.value
                parking_space['has_realtime_data'] = static_parking_site_input.has_realtime_data
                parking_spot_dicts.append(parking_space)

        for parking_spot_dict in parking_spot_dicts:
            try:
                static_parking_spot_inputs.append(
                    self.p_m_sensade_parking_lot_parking_space_validator.validate(parking_spot_dict)
                )
            except ValidationError as e:
                import_parking_spot_exceptions.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=parking_spot_dict.get('id'),
                        message=f'validation error for {parking_spot_dict}: {e.to_dict()}',
                    ),
                )

        return static_parking_spot_inputs, import_parking_spot_exceptions

    def _get_raw_static_parking_sites(
        self,
    ) -> tuple[list[PMSensadeParkingLot], list[ImportParkingSiteException]]:
        static_p_m_sensade_inputs: list[PMSensadeParkingLot] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        raw_parking_site_inputs, import_static_parking_site_exceptions = self.get_raw_parking_sites()
        import_parking_site_exceptions += import_static_parking_site_exceptions
        parking_site_dicts: list[dict] = []

        for raw_parking_site_input in raw_parking_site_inputs:
            response = self.request_get(
                url=f'{self.source_info.source_url}/parkinglot/parkinglot/{raw_parking_site_input.id}',
                headers={'Authorization': f'Bearer {self._request_token()}'},
                timeout=60,
            )
            parking_site_dicts.append(response.json()[0])

        for parking_site_dict in parking_site_dicts:
            try:
                static_p_m_sensade_inputs.append(self.p_m_sensade_parking_lot_validator.validate(parking_site_dict))
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('id'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return static_p_m_sensade_inputs, import_parking_site_exceptions

    def _get_raw_realtime_parking_sites(
        self,
    ) -> tuple[list[PMSensadeParkingLotStatus], list[ImportParkingSiteException]]:
        realtime_p_m_sensade_inputs: list[PMSensadeParkingLotStatus] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        raw_parking_site_inputs, import_static_parking_site_exceptions = self.get_raw_parking_sites()
        import_parking_site_exceptions += import_static_parking_site_exceptions
        parking_site_dicts: list[dict] = []

        for raw_parking_site_input in raw_parking_site_inputs:
            response = self.request_get(
                url=f'{self.source_info.source_url}/parkinglot/parkinglot/getcurrentparkinglotstatus/{raw_parking_site_input.id}',
                headers={'Authorization': f'Bearer {self._request_token()}'},
                timeout=60,
            )
            parking_site_dicts.append(response.json())

        for parking_site_dict in parking_site_dicts:
            try:
                realtime_p_m_sensade_inputs.append(
                    self.p_m_sensade_parking_lot_status_validator.validate(parking_site_dict)
                )
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('parkingLotId'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return realtime_p_m_sensade_inputs, import_parking_site_exceptions

    def get_raw_parking_sites(
        self,
    ) -> tuple[list[PMSensadeParkingLotsInput], list[ImportParkingSiteException]]:
        raw_p_m_sensade_inputs: list[PMSensadeParkingLotsInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(
            url=f'{self.source_info.source_url}/parkinglot/parkinglot',
            headers={'Authorization': f'Bearer {self._request_token()}'},
            timeout=60,
        )

        try:
            parking_site_dicts = self.p_m_sensade_parking_lots_input_validator.validate(response.json()[0])
        except ValidationError as e:
            import_parking_site_exceptions.append(
                ImportParkingSiteException(
                    source_uid=self.source_info.uid,
                    parking_site_uid='mobidatabw',
                    message=f'validation error for {parking_site_dicts}: {e.to_dict()}',
                ),
            )

        for parking_site_dict in parking_site_dicts.parkingLots:
            try:
                raw_p_m_sensade_inputs.append(self.p_m_sensade_parking_lot_input_validator.validate(parking_site_dict))
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('id'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return raw_p_m_sensade_inputs, import_parking_site_exceptions

    def _request_token(self) -> str:
        response = self.request_post(
            url=f'{self.source_info.source_url}/auth/login',
            headers={
                'Content-Type': 'application/json-patch+json',
                'accept': 'text/plain',
            },
            json={
                'email': self.config_helper.get('PARK_API_P_M_SENSADE_EMAIL'),
                'password': self.config_helper.get('PARK_API_P_M_SENSADE_PASSWORD'),
            },
            timeout=30,
        )
        return response.text
