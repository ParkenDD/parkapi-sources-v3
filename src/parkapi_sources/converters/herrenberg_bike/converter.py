"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import GeojsonInput, RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import HerrenbergBikeFeatureInput


class HerrenbergBikePullConverter(PullConverter):
    geojson_validator = DataclassValidator(GeojsonInput)
    herrenberg_feature_validator = DataclassValidator(HerrenbergBikeFeatureInput)

    source_info = SourceInfo(
        uid='herrenberg_bike',
        name='Stadt Herrenberg - Munigrid: Fahrrad-Abstellanlagen',
        public_url='https://www.munigrid.de/hbg/dataset/8',
        source_url='https://www.munigrid.de/api/file/11/latest',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Herrenberg - Munigrid',
        attribution_license='CC 0 1.0',
        attribution_url='https://creativecommons.org/publicdomain/zero/1.0/',
        has_realtime_data=False,
    )

    def _get_feature_inputs(self) -> tuple[list[HerrenbergBikeFeatureInput], list[ImportParkingSiteException]]:
        feature_inputs: list[HerrenbergBikeFeatureInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(url=self.source_info.source_url, timeout=30)
        response_data = response.json()

        try:
            geojson_input = self.geojson_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid Input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

        for feature_dict in geojson_input.features:
            if self._should_ignore_dataset(feature_dict):
                continue

            try:
                feature_input = self.herrenberg_feature_validator.validate(feature_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=feature_dict.get('properties', {}).get('id'),
                        message=f'Invalid data at uid {feature_dict.get("properties", {}).get("id")}: '
                        f'{e.to_dict()}, data: {feature_dict}',
                    ),
                )
                continue

            feature_inputs.append(feature_input)

        return feature_inputs, import_parking_site_exceptions

    def _should_ignore_dataset(self, feature_dict: dict) -> bool:
        if self.config_helper.get('PARK_API_HERRENBERG_BIKE_IGNORE_MISSING_CAPACITIES'):
            return feature_dict.get('properties', {}).get('capacity') is None

        return False

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        feature_inputs, import_parking_site_exceptions = self._get_feature_inputs()

        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        for feature_input in feature_inputs:
            static_parking_site_inputs.append(feature_input.to_static_parking_site_input())

        return static_parking_site_inputs, import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []
