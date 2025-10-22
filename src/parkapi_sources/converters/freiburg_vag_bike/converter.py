"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSiteInput

from .models import FreiburgVAGBikeFeatureInput


class FreiburgVAGBikePullConverter(ParkingSitePullConverter):
    geojson_validator = DataclassValidator(GeojsonInput)
    geojson_feature_validator = DataclassValidator(FreiburgVAGBikeFeatureInput)

    source_info = SourceInfo(
        uid='freiburg_vag_bike',
        name='Freiburger Verkehrs-AG Fahrradboxen',
        public_url='https://www.vag-freiburg.de/mehr-mobilitaet/mehr-fahrrad/fahrradboxen',
        source_url=(
            'https://geoportal.freiburg.de/wfs/vag_infra/vag_infra?SERVICE=WFS&version=2.0.0&REQUEST=GetFeature'
            '&typename=fahrradboxen&outputFormat=geojson&srsname=epsg:4326'
        ),
        timezone='Europe/Berlin',
        attribution_contributor='Freiburger Verkehrs-AG',
        has_realtime_data=False,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(url=self.source_info.source_url, timeout=30)
        response_data = response.json()

        try:
            geojson_input: GeojsonInput = self.geojson_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

        for feature_dict in geojson_input.features:
            properties = feature_dict.get('properties', {})
            capacity_charging = properties.get('capacity_charging')
            if isinstance(capacity_charging, str) and capacity_charging.strip().lower() == 'nein':
                properties['capacity_charging'] = 0
            try:
                feature_input = self.geojson_feature_validator.validate(feature_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=str(feature_dict.get('properties', {}).get('original_uid')),
                        message=(
                            'Invalid data at uid '
                            f'{feature_dict.get("properties", {}).get("original_uid")}: {e.to_dict()}, data: {feature_dict}'
                        ),
                    ),
                )
                continue

            static_parking_site_inputs.append(feature_input.to_static_parking_site_input())

        return static_parking_site_inputs, import_parking_site_exceptions
