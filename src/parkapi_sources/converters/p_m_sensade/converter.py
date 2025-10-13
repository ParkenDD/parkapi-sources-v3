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
        public_url='https://sensade.com/',
        source_url='https://api.sensade.com',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        static_p_m_sensade_inputs, import_parking_site_exceptions = self._get_static_sensade_parking_lots()

        for static_p_m_sensade_input in static_p_m_sensade_inputs:
            static_parking_site_inputs.append(static_p_m_sensade_input.to_static_parking_site_input())

        return static_parking_site_inputs, import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        realtime_p_m_sensade_inputs, import_parking_site_exceptions = self._get_realtime_sensade_parking_lots()

        for realtime_p_m_sensade_input in realtime_p_m_sensade_inputs:
            realtime_parking_site_inputs.append(realtime_p_m_sensade_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def get_static_parking_spots(
        self,
    ) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[PMSensadeParkingLotParkingSpace] = []
        import_parking_spot_exceptions: list[ImportParkingSpotException] = []

        static_sensade_parking_lots, import_parking_site_exceptions = self._get_static_sensade_parking_lots()
        import_parking_spot_exceptions += [
            ImportParkingSpotException(
                source_uid=exceptions.source_uid,
                parking_spot_uid=getattr(exceptions, 'parking_site_uid', None),
                message=exceptions.message,
            )
            for exceptions in import_parking_site_exceptions
        ]

        for static_sensade_parking_lot in static_sensade_parking_lots:
            for parking_space in static_sensade_parking_lot.parkingSpaces:
                try:
                    parking_space_input = self.p_m_sensade_parking_lot_parking_space_validator.validate(parking_space)
                    static_parking_spot_inputs.append(
                        parking_space_input.to_static_parking_spot_input(static_sensade_parking_lot)
                    )
                except ValidationError as e:
                    import_parking_spot_exceptions.append(
                        ImportParkingSpotException(
                            source_uid=self.source_info.uid,
                            parking_spot_uid=parking_space.get('id'),
                            message=f'validation error for {parking_space}: {e.to_dict()}',
                        ),
                    )

        return static_parking_spot_inputs, import_parking_spot_exceptions

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        return [], []

    def _get_static_sensade_parking_lots(
        self,
    ) -> tuple[list[PMSensadeParkingLot], list[ImportParkingSiteException]]:
        static_sensade_parking_lots: list[PMSensadeParkingLot] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        sensade_parking_lots, import_sensade_parking_site_exceptions = self._get_sensade_parking_lots()
        import_parking_site_exceptions += import_sensade_parking_site_exceptions
        parking_site_dicts: list[dict] = []

        for sensade_parking_lot in sensade_parking_lots:
            response = self.request_get(
                url=f'{self.source_info.source_url}/parkinglot/parkinglot/{sensade_parking_lot.id}',
                headers={'Authorization': f'Bearer {self._request_token()}'},
                timeout=60,
            )
            parking_site_dicts.append(response.json()[0])

        for parking_site_dict in parking_site_dicts:
            try:
                static_sensade_parking_lots.append(self.p_m_sensade_parking_lot_validator.validate(parking_site_dict))
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('id'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return static_sensade_parking_lots, import_parking_site_exceptions

    def _get_realtime_sensade_parking_lots(
        self,
    ) -> tuple[list[PMSensadeParkingLotStatus], list[ImportParkingSiteException]]:
        realtime_sensade_parking_lots: list[PMSensadeParkingLotStatus] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        sensade_parking_lots, import_sensade_parking_site_exceptions = self._get_sensade_parking_lots()
        import_parking_site_exceptions += import_sensade_parking_site_exceptions
        parking_site_dicts: list[dict] = []

        for sensade_parking_lot in sensade_parking_lots:
            response = self.request_get(
                url=f'{self.source_info.source_url}/parkinglot/parkinglot/getcurrentparkinglotstatus/{sensade_parking_lot.id}',
                headers={'Authorization': f'Bearer {self._request_token()}'},
                timeout=60,
            )
            parking_site_dicts.append(response.json())

        for parking_site_dict in parking_site_dicts:
            try:
                realtime_sensade_parking_lots.append(
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

        return realtime_sensade_parking_lots, import_parking_site_exceptions

    def _get_sensade_parking_lots(
        self,
    ) -> tuple[list[PMSensadeParkingLotsInput], list[ImportParkingSiteException]]:
        sensade_parking_lots: list[PMSensadeParkingLotsInput] = []
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
                sensade_parking_lots.append(self.p_m_sensade_parking_lot_input_validator.validate(parking_site_dict))
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('id'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return sensade_parking_lots, import_parking_site_exceptions

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
