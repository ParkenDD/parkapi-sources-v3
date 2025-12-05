"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import HeilbronnGoldbeckFacilitiesInput, HeilbronnGoldbeckOccupanciesInput


class HeilbronnGoldbeckPullConverter(ParkingSitePullConverter):
    required_config_keys = [
        'PARK_API_HEILBRONN_GOLDBECK_USERNAME',
        'PARK_API_HEILBRONN_GOLDBECK_PASSWORD',
    ]

    heilbronn_goldbeck_occupancies_validator = DataclassValidator(HeilbronnGoldbeckOccupanciesInput)
    heilbronn_goldbeck_facilities_validator = DataclassValidator(HeilbronnGoldbeckFacilitiesInput)

    source_info = SourceInfo(
        uid='heilbronn_goldbeck',
        name='Stadtwerke Heilbronn E-Quartiersgarage from Goldbeck API',
        public_url='https://www.stadtwerke-heilbronn.de/swh/parken-und-laden/parken/',
        source_url='https://control.goldbeck-parking.de',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        raw_realtime_parking_site_inputs, realtime_parking_site_errors = self._get_raw_realtime_parking_sites()
        raw_realtime_parking_site_by_id: dict[int, HeilbronnGoldbeckOccupanciesInput] = {
            raw_realtime_input.facilityId: raw_realtime_input for raw_realtime_input in raw_realtime_parking_site_inputs
        }

        raw_static_parking_site_inputs, static_parking_site_errors = self._get_raw_static_parking_sites(
            raw_realtime_parking_site_by_id
        )
        import_parking_site_exceptions = static_parking_site_errors + realtime_parking_site_errors

        for raw_static_input in raw_static_parking_site_inputs:
            raw_realtime_input = raw_realtime_parking_site_by_id.get(raw_static_input.id)
            static_parking_site_inputs.append(
                raw_static_input.to_static_parking_site_input(
                    raw_realtime_input,
                ),
            )

        return static_parking_site_inputs, import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        raw_realtime_parking_site_inputs, import_parking_site_exceptions = self._get_raw_realtime_parking_sites()

        for raw_realtime_input in raw_realtime_parking_site_inputs:
            realtime_parking_site_input = raw_realtime_input.to_realtime_parking_site_input()
            if realtime_parking_site_input is None:
                continue

            realtime_parking_site_inputs.append(realtime_parking_site_input)

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _get_raw_static_parking_sites(
        self,
        raw_realtime_parking_site_by_id: dict[int, HeilbronnGoldbeckOccupanciesInput],
    ) -> tuple[list[HeilbronnGoldbeckFacilitiesInput], list[ImportParkingSiteException]]:
        heilbronn_goldbeck_facilities_inputs: list[HeilbronnGoldbeckFacilitiesInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(
            url=f'{self.source_info.source_url}/ipaw/services/v4x0/facilities?address=true&position=true&tariffs=true',
            timeout=30,
            auth=(
                self.config_helper.get('PARK_API_HEILBRONN_GOLDBECK_USERNAME'),
                self.config_helper.get('PARK_API_HEILBRONN_GOLDBECK_PASSWORD'),
            ),
        )
        parking_site_dicts = response.json()

        for parking_site_dict in parking_site_dicts:
            facility_id = parking_site_dict.get('id')
            raw_realtime_input = raw_realtime_parking_site_by_id.get(facility_id)
            if raw_realtime_input is None:
                continue

            total_counter = raw_realtime_input.get_total_counter()
            if total_counter is None:
                continue

            try:
                heilbronn_goldbeck_facilities_inputs.append(
                    self.heilbronn_goldbeck_facilities_validator.validate(parking_site_dict)
                )
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('id'),
                        message=f'validation error for data {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return heilbronn_goldbeck_facilities_inputs, import_parking_site_exceptions

    def _get_raw_realtime_parking_sites(
        self,
    ) -> tuple[list[HeilbronnGoldbeckOccupanciesInput], list[ImportParkingSiteException]]:
        heilbronn_goldbeck_occupancies_inputs: list[HeilbronnGoldbeckOccupanciesInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(
            url=f'{self.source_info.source_url}/ipaw/services/v4x0/occupancies',
            timeout=30,
            auth=(
                self.config_helper.get('PARK_API_HEILBRONN_GOLDBECK_USERNAME'),
                self.config_helper.get('PARK_API_HEILBRONN_GOLDBECK_PASSWORD'),
            ),
        )
        parking_site_dicts = response.json()
        for parking_site_dict in parking_site_dicts:
            counters = parking_site_dict.get('counters') or []
            parking_site_dict['counters'] = [c for c in counters if c.get('type', {}).get('type') == 'TOTAL']

            try:
                heilbronn_goldbeck_occupancies_inputs.append(
                    self.heilbronn_goldbeck_occupancies_validator.validate(parking_site_dict)
                )
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('facilityId'),
                        message=f'validation error for data {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return heilbronn_goldbeck_occupancies_inputs, import_parking_site_exceptions
