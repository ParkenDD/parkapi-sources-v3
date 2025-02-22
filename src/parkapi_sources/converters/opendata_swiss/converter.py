"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import GeojsonInput, RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import OpenDataSwissFeatureInput


class OpenDataSwissPullConverter(PullConverter):
    geojson_validator = DataclassValidator(GeojsonInput)
    opendata_swiss_feature_validator = DataclassValidator(OpenDataSwissFeatureInput)

    source_info = SourceInfo(
        uid='opendata_swiss',
        name='Open-Data-Plattform öV Schweiz (opentransport.swiss)',
        public_url='https://data.opentransportdata.swiss/de/dataset/parking-facilities',
        source_url='https://data.opentransportdata.swiss/de/dataset/parking-facilities/permalink',
        timezone='Europe/Berlin',
        attribution_contributor='Schweizerische Bundesbahnen (SBB) AG',
        has_realtime_data=False,
    )

    def _get_feature_inputs(self) -> tuple[list[OpenDataSwissFeatureInput], list[ImportParkingSiteException]]:
        feature_inputs: list[OpenDataSwissFeatureInput] = []
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
            try:
                feature_input = self.opendata_swiss_feature_validator.validate(feature_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=feature_dict.get('id'),
                        message=f'Invalid data at uid {feature_dict.get("id")}: {e.to_dict()}, data: {feature_dict}',
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
        return [], []  # ATM only static data can be called from the Platform
