"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import (
    ParkingSitePullConverter,
    StaticGeojsonDataMixin,
)
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import AalenInput


class AalenPullConverter(ParkingSitePullConverter, StaticGeojsonDataMixin):
    aalen_realtime_update_validator = DataclassValidator(AalenInput)
    source_info = SourceInfo(
        uid='aalen',
        name='Stadtwerke Aalen GmbH',
        public_url='https://www.sw-aalen.de/privatkunden/dienstleistungen/parken/parkhaeuser',
        source_url='https://www.sw-aalen.de/privatkunden/dienstleistungen/parken/parkhausbelegung.json',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_static_parking_site_inputs_and_exceptions(source_uid=self.source_info.uid)

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        realtime_aalen_inputs, import_parking_site_exceptions = self._get_raw_realtime_parking_sites()

        for realtime_aalen_input in realtime_aalen_inputs:
            realtime_parking_site_inputs.append(realtime_aalen_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _get_raw_realtime_parking_sites(self) -> tuple[list[AalenInput], list[ImportParkingSiteException]]:
        realtime_raw_parking_site_inputs: list[AalenInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(url=self.source_info.source_url, timeout=60)
        parking_site_dicts = response.json()

        for parking_site_dict in parking_site_dicts:
            try:
                realtime_raw_parking_site_inputs.append(
                    self.aalen_realtime_update_validator.validate(parking_site_dict)
                )
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('name'),
                        message=f'Invalid data at uid {parking_site_dict.get("name")}: '
                        f'{e.to_dict()}, data: {parking_site_dict}',
                    ),
                )
                continue

        return realtime_raw_parking_site_inputs, import_parking_site_exceptions
