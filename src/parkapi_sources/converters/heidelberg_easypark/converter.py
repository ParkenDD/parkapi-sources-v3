"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSiteInput

from .validator import HeidelbergEasyParkParkingSiteInput


class HeidelbergEasyParkPullConverter(ParkingSitePullConverter):
    source_info = SourceInfo(
        uid='heidelberg_easypark',
        name='Heidelberg EasyPark',
        source_url='https://ckan.datenplattform.heidelberg.de/de/dataset/fecde4f4-41c0-4c3b-b763-41a84dad39f8/resource'
        '/12e9e778-880a-49a9-90cc-2fbb615f2da6/download/inventory_data_offset-1.json',
        has_realtime_data=False,
    )
    geojson_validator = DataclassValidator(GeojsonInput)
    heidelberg_parking_site_validator = DataclassValidator(HeidelbergEasyParkParkingSiteInput)

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_sites: list[StaticParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        static_data_updated_at = datetime.now(timezone.utc)
        response = self.request_get(
            url=self.source_info.source_url,
            timeout=30,
        )

        parking_sites_input: GeojsonInput = self.geojson_validator.validate(response.json())

        for parking_site_dict in parking_sites_input.features:
            try:
                heidelberg_parking_site_input = self.heidelberg_parking_site_validator.validate(parking_site_dict)
                static_parking_site = heidelberg_parking_site_input.to_static_parking_site(
                    static_data_updated_at=static_data_updated_at,
                )
                if static_parking_site is None:
                    continue
                static_parking_sites.append(static_parking_site)

            except ValidationError as e:
                uid: str | None = parking_site_dict.get('properties', {}).get('Segment')
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=str(uid) if uid else None,
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return self.apply_static_patches(static_parking_sites), parking_site_errors
