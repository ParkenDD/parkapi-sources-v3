"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import GeojsonInput, RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import KarlsruheBikeFeatureInput, KarlsruheFeatureInput


class KarlsruheBasePullConverter(PullConverter, ABC):
    geojson_validator = DataclassValidator(GeojsonInput)
    karlsruhe_feature_validator: DataclassValidator

    def _get_feature_inputs(self) -> tuple[list[KarlsruheFeatureInput], list[ImportParkingSiteException]]:
        feature_inputs: list[KarlsruheFeatureInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        # Karlsruhes http-server config misses the intermediate cert GeoTrust TLS RSA CA G1, so we add it here manually.
        ca_path = Path(Path(__file__).parent, 'files', 'ca.crt.pem')
        response = self.request_get(url=self.source_info.source_url, verify=str(ca_path), timeout=30)

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
                feature_input = self.karlsruhe_feature_validator.validate(feature_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=feature_dict.get('properties').get('id'),
                        message=f'Invalid data at uid {feature_dict.get("properties").get("id")}: {e.to_dict()}, '
                        f'data: {feature_dict}',
                    ),
                )
                continue

            feature_inputs.append(feature_input)

        return feature_inputs, import_parking_site_exceptions

    @abstractmethod
    def _should_ignore_dataset(self, feature_dict: dict) -> bool:
        pass

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        feature_inputs, import_parking_site_exceptions = self._get_feature_inputs()

        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        for feature_input in feature_inputs:
            static_parking_site_inputs.append(feature_input.to_static_parking_site_input())

        return static_parking_site_inputs, import_parking_site_exceptions


class KarlsruhePullConverter(KarlsruheBasePullConverter):
    karlsruhe_feature_validator = DataclassValidator(KarlsruheFeatureInput)

    source_info = SourceInfo(
        uid='karlsruhe',
        name='Stadt Karlsruhe: PKW-Parkplätze',
        public_url='https://web1.karlsruhe.de/service/Parken/',
        source_url='https://mobil.trk.de/geoserver/TBA/ows?service=WFS&version=1.0.0&request=GetFeature'
        '&typeName=TBA%3Aparkhaeuser&outputFormat=application%2Fjson&srsName=EPSG:4326',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Karlsruhe',
        attribution_license='Creative Commons Namensnennung - 4.0 International (CC-BY 4.0)',
        attribution_url='http://creativecommons.org/licenses/by/4.0/',
        has_realtime_data=True,
    )

    def _should_ignore_dataset(self, feature_dict: dict) -> bool:
        return False

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        feature_inputs, import_parking_site_exceptions = self._get_feature_inputs()

        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        for feature_input in feature_inputs:
            realtime_parking_site_input = feature_input.to_realtime_parking_site_input()
            if realtime_parking_site_input is not None:
                realtime_parking_site_inputs.append(realtime_parking_site_input)

        return realtime_parking_site_inputs, import_parking_site_exceptions


class KarlsruheBikePullConverter(KarlsruheBasePullConverter):
    karlsruhe_feature_validator = DataclassValidator(KarlsruheBikeFeatureInput)

    source_info = SourceInfo(
        uid='karlsruhe_bike',
        name='Stadt Karlsruhe: Fahrrad-Abstellanlagen',
        public_url='https://web1.karlsruhe.de/service/Parken/',
        source_url='https://mobil.trk.de/geoserver/TBA/ows?service=WFS&version=1.0.0&request=GetFeature'
        '&typeName=TBA%3Afahrradanlagen&outputFormat=application%2Fjson&srsName=EPSG:4326',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Karlsruhe',
        attribution_license='Creative Commons Namensnennung - 4.0 International (CC-BY 4.0)',
        attribution_url='http://creativecommons.org/licenses/by/4.0/',
        has_realtime_data=False,
    )

    def _should_ignore_dataset(self, feature_dict: dict) -> bool:
        if self.config_helper.get('PARK_API_KARLSRUHE_BIKE_IGNORE_MISSING_CAPACITIES'):
            return feature_dict.get('properties', {}).get('stellplaetze') is None

        return False

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []
