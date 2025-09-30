"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import (
    ParkingSitePullConverter,
)
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    SourceInfo,
    StaticParkingSiteInput,
)

from .validators import (
    PMSensadeParkingLot,
    PMSensadeParkingLotInput,
    PMSensadeParkingLotsInput,
    PMSensadeParkingLotStatus,
)


class PMSensadePullConverter(ParkingSitePullConverter):
    required_config_keys = [
        'PARK_API_P_M_SENSADE_EMAIL',
        'PARK_API_P_M_SENSADE_PASSWORD',
    ]
    p_m_sensade_parking_lot_validator = DataclassValidator(PMSensadeParkingLot)
    p_m_sensade_parking_lots_input_validator = DataclassValidator(PMSensadeParkingLotsInput)
    p_m_sensade_parking_lot_input_validator = DataclassValidator(PMSensadeParkingLotInput)
    p_m_sensade_parking_lot_status_validator = DataclassValidator(PMSensadeParkingLotStatus)

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
            organization_id = parking_site_dicts.organizationId
        except ValidationError as e:
            import_parking_site_exceptions.append(
                ImportParkingSiteException(
                    source_uid=self.source_info.uid,
                    parking_site_uid=organization_id,
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
            data={
                'email': self.config_helper.get('PARK_API_P_M_SENSADE_EMAIL'),
                'password': self.config_helper.get('PARK_API_P_M_SENSADE_PASSWORD'),
            },
            timeout=30,
        )
        token_data = response.json()
        return token_data['access_token']
