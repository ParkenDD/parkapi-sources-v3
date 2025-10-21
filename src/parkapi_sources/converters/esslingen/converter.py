"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pyproj
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.push import JsonConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSiteInput

from .validator import EsslingenParkingSiteFeatureInput


class EsslingenPushConverter(JsonConverter, ParkingSiteBaseConverter):
    source_info = SourceInfo(
        uid='esslingen',
        name='Esslingen',
        has_realtime_data=False,
    )
    geojson_validator = DataclassValidator(GeojsonInput)
    esslingen_parking_site_validator = DataclassValidator(EsslingenParkingSiteFeatureInput)
    proj: pyproj.Proj = pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True)

    def handle_json(self, data: dict | list) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_sites: list[StaticParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        parking_sites_input: GeojsonInput = self.geojson_validator.validate(data)

        for parking_site_dict in parking_sites_input.features:
            try:
                esslingen_parking_site_input = self.esslingen_parking_site_validator.validate(parking_site_dict)
                static_parking_site = esslingen_parking_site_input.to_static_parking_site()
                if static_parking_site is None:
                    continue
                static_parking_sites.append(static_parking_site)

            except ValidationError as e:
                uid: str | None = parking_site_dict.get('properties', {}).get('fid')
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=str(uid) if uid else None,
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return static_parking_sites, parking_site_errors
