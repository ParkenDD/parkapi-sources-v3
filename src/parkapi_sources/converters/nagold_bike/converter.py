"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.push import JsonConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSiteInput
from parkapi_sources.util.dict import AnyDict

from .validator import NagoldBikeFeatureInput


class NagoldBikePushConverter(JsonConverter, ParkingSiteBaseConverter):
    source_info = SourceInfo(
        uid='nagold_bike',
        name='Stadt Nagold: Fahrrad-Abstellanlagen',
        public_url='https://www.nagold.de/',
        has_realtime_data=False,
    )
    geojson_validator = DataclassValidator(GeojsonInput)
    nagold_bike_validator = DataclassValidator(NagoldBikeFeatureInput)

    def handle_json(self, data: dict | list) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_sites: list[StaticParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        parking_sites_input: GeojsonInput = self.geojson_validator.validate(data)

        for parking_site_dict in parking_sites_input.features:
            if self._is_placeholder(parking_site_dict.get('properties', {})):
                continue

            try:
                nagold_bike_input = self.nagold_bike_validator.validate(parking_site_dict)
                static_parking_sites += nagold_bike_input.to_static_parking_sites()

            except ValidationError as e:
                uid: Any = parking_site_dict.get('properties', {}).get('OBJECTID')
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=str(uid) if uid else None,
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return static_parking_sites, parking_site_errors

    @staticmethod
    def _is_placeholder(properties: AnyDict) -> bool:
        """
        The dataset contains placeholder features without a stand type and without any capacity. These are surveying
        artifacts and not actual bike parking installations, therefore they are ignored instead of reported as errors.
        """
        return not str(properties.get('Stellplatz') or '').strip() and not properties.get('Anzahl_Bue')
