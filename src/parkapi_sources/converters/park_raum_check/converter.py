"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.push import JsonConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSiteInput

from .validators import KehlFeatureInput, SachsenheimFeatureInput


class ParkRaumCheckBasePushConverter(JsonConverter, ParkingSiteBaseConverter, ABC):
    geojson_validator = DataclassValidator(GeojsonInput)

    @property
    @abstractmethod
    def parking_site_validator(self) -> DataclassValidator: ...

    def handle_json(self, data: dict | list) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_sites: list[StaticParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        static_data_updated_at = datetime.now(timezone.utc)

        parking_site_inputs: GeojsonInput = self.geojson_validator.validate(data)

        for parking_site_dict in parking_site_inputs.features:
            # Ignore private parking as it lacks all data
            if parking_site_dict.get('properties', {}).get('Widmung') in ['privat', None]:
                continue
            try:
                heidelberg_parking_site_input = self.parking_site_validator.validate(parking_site_dict)
                static_parking_site = heidelberg_parking_site_input.to_static_parking_site(
                    static_data_updated_at=static_data_updated_at,
                )
                if static_parking_site is None:
                    continue
                static_parking_sites.append(static_parking_site)

            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('id'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return static_parking_sites, parking_site_errors


class ParkRaumCheckKehlPushConverter(ParkRaumCheckBasePushConverter):
    source_info = SourceInfo(
        uid='park_raum_check_kehl',
        name='Stadt Kehl: ParkRaumCheck',
        has_realtime_data=False,
    )
    parking_site_validator = DataclassValidator(KehlFeatureInput)


class ParkRaumCheckSachsenheimPushConverter(ParkRaumCheckBasePushConverter):
    source_info = SourceInfo(
        uid='park_raum_check_sachsenheim',
        name='Stadt Sachsenheim: ParkRaumCheck',
        has_realtime_data=False,
    )
    parking_site_validator = DataclassValidator(SachsenheimFeatureInput)
