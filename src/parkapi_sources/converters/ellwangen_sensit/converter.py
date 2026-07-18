"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import EllwangenSensitParkingLotInput


class EllwangenSensitPullConverter(ParkingSitePullConverter):
    required_config_keys = [
        'PARK_API_ELLWANGEN_SENSIT_USER',
        'PARK_API_ELLWANGEN_SENSIT_PASSWORD',
    ]

    ellwangen_sensit_parking_lot_validator = DataclassValidator(EllwangenSensitParkingLotInput)

    source_info = SourceInfo(
        uid='ellwangen_sensit',
        name='Ellwangen Parkplätze (Sensit)',
        public_url='https://ellwangen.nedapparking.com',
        source_url='https://ellwangen.nedapparking.com/api/v1/parkingLots',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        raw_parking_lot_inputs, import_parking_site_exceptions = self._get_raw_parking_lots()

        static_data_updated_at = datetime.now(tz=timezone.utc)
        for raw_parking_lot_input in raw_parking_lot_inputs:
            static_parking_site_inputs.append(
                raw_parking_lot_input.to_static_parking_site_input(static_data_updated_at),
            )

        return self.apply_static_patches(static_parking_site_inputs), import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        raw_parking_lot_inputs, import_parking_site_exceptions = self._get_raw_parking_lots()

        realtime_data_updated_at = datetime.now(tz=timezone.utc)
        for raw_parking_lot_input in raw_parking_lot_inputs:
            realtime_parking_site_inputs.append(
                raw_parking_lot_input.to_realtime_parking_site_input(realtime_data_updated_at),
            )

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _get_raw_parking_lots(
        self,
    ) -> tuple[list[EllwangenSensitParkingLotInput], list[ImportParkingSiteException]]:
        raw_parking_lot_inputs: list[EllwangenSensitParkingLotInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(
            url=self.source_info.source_url,
            auth=(
                self.config_helper.get('PARK_API_ELLWANGEN_SENSIT_USER'),
                self.config_helper.get('PARK_API_ELLWANGEN_SENSIT_PASSWORD'),
            ),
        )
        parking_lot_dicts = response.json()

        for parking_lot_dict in parking_lot_dicts:
            try:
                raw_parking_lot_inputs.append(self.ellwangen_sensit_parking_lot_validator.validate(parking_lot_dict))
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_lot_dict.get('id'),
                        message=f'validation error for data {parking_lot_dict}: {e.to_dict()}',
                    ),
                )

        return raw_parking_lot_inputs, import_parking_site_exceptions
