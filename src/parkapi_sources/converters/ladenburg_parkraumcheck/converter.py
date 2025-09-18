"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.push import JsonConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSiteInput

from .validator import LadenburgParkraumcheckParkingSiteInput


class LadenburgParkraumcheckPushConverter(JsonConverter, ParkingSiteBaseConverter):
    source_info = SourceInfo(
        uid='ladenburg_parkraumcheck',
        name='Ladenburg: Parkraumcheck',
        has_realtime_data=False,
    )
    geojson_validator = DataclassValidator(GeojsonInput)
    ladenburg_parkraumcheck_validator = DataclassValidator(LadenburgParkraumcheckParkingSiteInput)

    def handle_json(self, data: dict | list) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_sites: list[StaticParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        parking_sites_input: GeojsonInput = self.geojson_validator.validate(data)
        static_data_updated_at = datetime.now(timezone.utc)

        for parking_site_dict in parking_sites_input.features:
            try:
                ladenburg_parkraumcheck_parking_site_input = self.ladenburg_parkraumcheck_validator.validate(
                    parking_site_dict,
                )
                static_parking_site = ladenburg_parkraumcheck_parking_site_input.to_static_parking_site(
                    static_data_updated_at=static_data_updated_at,
                )
                if static_parking_site is None:
                    continue
                static_parking_sites.append(static_parking_site)

            except ValidationError as e:
                uid: int | None = parking_site_dict.get('properties', {}).get('fid')
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=str(uid) if uid else None,
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return static_parking_sites, parking_site_errors
