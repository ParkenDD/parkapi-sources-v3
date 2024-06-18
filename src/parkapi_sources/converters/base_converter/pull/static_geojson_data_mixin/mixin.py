"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests import ConnectionError, JSONDecodeError
from urllib3.exceptions import NewConnectionError
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull.static_geojson_data_mixin.models import GeojsonFeatureInput, GeojsonInput
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput
from parkapi_sources.util import ConfigHelper


class StaticGeojsonDataMixin:
    config_helper: ConfigHelper
    source_info: SourceInfo
    geojson_validator = DataclassValidator(GeojsonInput)
    geojson_feature_validator = DataclassValidator(GeojsonFeatureInput)
    _base_url = 'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/main/sources'

    def _get_static_geojson(self, source_uid: str) -> GeojsonInput:
        if self.config_helper.get('STATIC_GEOJSON_BASE_PATH'):
            with Path(self.config_helper.get('STATIC_GEOJSON_BASE_PATH'), f'{source_uid}.geojson').open() as geojson_file:
                return json.loads(geojson_file.read())
        else:
            try:
                response = requests.get(f'{self.config_helper.get("STATIC_GEOJSON_BASE_URL")}/{source_uid}.geojson', timeout=30)
            except (ConnectionError, NewConnectionError) as e:
                raise ImportParkingSiteException(
                    source_uid=self.source_info.uid,
                    message='Connection issue for GeoJSON data',
                ) from e
            try:
                return response.json()
            except JSONDecodeError as e:
                raise ImportParkingSiteException(
                    source_uid=self.source_info.uid,
                    message='Invalid JSON response for GeoJSON data',
                ) from e

    def _get_static_parking_site_inputs_and_exceptions(
        self,
        source_uid: str,
    ) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        geojson_dict = self._get_static_geojson(source_uid)
        try:
            geojson_input = self.geojson_validator.validate(geojson_dict)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=source_uid,
                message=f'Invalid GeoJSON for source {source_uid}: {e.to_dict()}. Data: {geojson_dict}',
            ) from e

        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        for feature_dict in geojson_input.features:
            try:
                feature_input: GeojsonFeatureInput = self.geojson_feature_validator.validate(feature_dict)
                static_parking_site_inputs.append(
                    feature_input.to_static_parking_site_input(
                        # TODO: Use the Last-Updated HTTP header instead, but as Github does not set such an header, we need to move
                        #  all GeoJSON data in order to use this.
                        static_data_updated_at=datetime.now(tz=timezone.utc),
                    ),
                )
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=feature_dict.get('properties', {}).get('uid'),
                        message=f'Invalid GeoJSON feature for source {source_uid}: {e.to_dict()}',
                    ),
                )
        return static_parking_site_inputs, import_parking_site_exceptions
