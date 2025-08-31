"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSpotPullConverter
from parkapi_sources.exceptions import ImportParkingSpotException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSpotInput

from .validator import HeidelbergDisabledParkingSpotInput


class HeidelbergDisabledPullConverter(ParkingSpotPullConverter):
    source_info = SourceInfo(
        uid='heidelberg_disabled',
        name='Stadt Heidelberg: Behindertenparkplätze',
        source_url='https://ckan.datenplattform.heidelberg.de/de/dataset/708df8e2-d452-483e-9e57-f04027d52a17/resource'
        '/6dc64728-65ba-47ed-bbe2-9e59b5dbaa0c/download/features_new.geojson',
        has_realtime_data=False,
    )
    geojson_validator = DataclassValidator(GeojsonInput)
    heidelberg_parking_spot_validator = DataclassValidator(HeidelbergDisabledParkingSpotInput)

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spots: list[StaticParkingSpotInput] = []
        parking_spot_errors: list[ImportParkingSpotException] = []

        static_data_updated_at = datetime.now(timezone.utc)
        response = self.request_get(
            url=self.source_info.source_url,
            timeout=30,
        )

        parking_spots_input: GeojsonInput = self.geojson_validator.validate(response.json())

        for parking_spot_dict in parking_spots_input.features:
            try:
                heidelberg_parking_site_input = self.heidelberg_parking_spot_validator.validate(parking_spot_dict)
                static_parking_site = heidelberg_parking_site_input.to_static_parking_site(
                    static_data_updated_at=static_data_updated_at,
                )
                if static_parking_site is None:
                    continue
                static_parking_spots.append(static_parking_site)

            except ValidationError as e:
                parking_spot_errors.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=parking_spot_dict.get('id'),
                        message=f'validation error for {parking_spot_dict}: {e.to_dict()}',
                    ),
                )

        return self.apply_static_patches(static_parking_spots), parking_spot_errors
