"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

import requests
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import GeojsonInput, PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import HerrenbergBikeFeatureInput


class HerrenbergBikePullConverter(PullConverter, ABC):
    geojson_validator = DataclassValidator(GeojsonInput)
    herrenberg_feature_validator = DataclassValidator(HerrenbergBikeFeatureInput)

    source_info = SourceInfo(
        uid='herrenberg_bike',
        name='Stadt Herrenberg - Munigrid: Fahrrad-Abstellanlagen',
        public_url='https://www.munigrid.de/hbg/dataset/8',
        source_url='https://r2.munigrid.de/11-d76db68da7d8354bb425c9eb90d6d78a.json',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Herrenberg - Munigrid',
        attribution_license='Datenlizenz Deutschland – Zero – Version 2.0 (DL-DE->Zero-2.0)',
        attribution_url='https://www.govdata.de/dl-de/zero-2-0',
        has_realtime_data=False,
    )

    def _get_feature_inputs(self) -> tuple[list[HerrenbergBikeFeatureInput], list[ImportParkingSiteException]]:
        feature_inputs: list[HerrenbergBikeFeatureInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = requests.get(self.source_info.source_url, timeout=30)
        response_data = response.json()

        try:
            geojson_input = self.geojson_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid Input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

        for feature_dict in geojson_input.features:
            try:
                feature_input = self.herrenberg_feature_validator.validate(feature_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=feature_dict.get('properties').get('id'),
                        message=f'Invalid data at uid {feature_dict.get("properties").get("id")}: ' f'{e.to_dict()}, data: {feature_dict}',
                    ),
                )
                continue

            feature_inputs.append(feature_input)

        return feature_inputs, import_parking_site_exceptions

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        feature_inputs, import_parking_site_exceptions = self._get_feature_inputs()

        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        for feature_input in feature_inputs:
            static_parking_site_inputs.append(feature_input.to_static_parking_site_input())

        return static_parking_site_inputs, import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []
