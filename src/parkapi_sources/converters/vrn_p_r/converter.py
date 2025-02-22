"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import GeojsonInput, RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import VrnParkAndRideFeaturesInput


class VrnParkAndRidePullConverter(PullConverter, ABC):
    list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    geojson_validator = DataclassValidator(GeojsonInput)
    vrn_p_r_feature_validator = DataclassValidator(VrnParkAndRideFeaturesInput)

    source_info = SourceInfo(
        uid='vrn_p_r',
        name='Verkehrsverbund Rhein-Neckar GmbH - P+R Parkplätze',
        public_url='https://www.vrn.de/opendata/datasets/pr-parkplaetze-mit-vrn-parksensorik',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )

    def _get_feature_inputs(self) -> tuple[list[VrnParkAndRideFeaturesInput], list[ImportParkingSiteException]]:
        feature_inputs: list[VrnParkAndRideFeaturesInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(
            url='https://spatial.vrn.de/data/rest/services/P_R_Sensorik__Realtime_/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson',
            timeout=30,
        )

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
                feature_input = self.vrn_p_r_feature_validator.validate(feature_dict)
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
        if self.config_helper.get('PARK_API_VRN_P_R_IGNORE_MISSING_CAPACITIES'):
            return feature_dict.get('properties', {}).get('capacity') is None
        return False

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        feature_inputs, import_parking_site_exceptions = self._get_feature_inputs()
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        for feature_input in feature_inputs:
            static_parking_site_inputs.append(feature_input.to_static_parking_site_input())

        return static_parking_site_inputs, import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        feature_inputs, import_parking_site_exceptions = self._get_feature_inputs()
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        for feature_input in feature_inputs:
            realtime_parking_site_inputs.append(feature_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions
