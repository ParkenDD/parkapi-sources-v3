"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSpotPullConverter
from parkapi_sources.exceptions import ImportParkingSpotException, ImportSourceException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSpotInput

from .models import KarlsruheDisabledFeatureInput


class KarlsruheDisabledPullConverter(ParkingSpotPullConverter):
    geojson_validator = DataclassValidator(GeojsonInput)
    geojson_feature_validator = DataclassValidator(KarlsruheDisabledFeatureInput)

    source_info = SourceInfo(
        uid='karlsruhe_disabled',
        name='Stadt Karlsruhe: Behindertenparkplätze',
        source_url='https://mobil.trk.de/geoserver/TBA/ows?service=WFS&version=1.0.0&request=GetFeature'
        '&srsname=EPSG:4326&typeName=TBA%3Abehinderten_parkplaetze&outputFormat=application%2Fjson',
        has_realtime_data=False,
    )

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[StaticParkingSpotInput] = []
        import_parking_spot_exceptions: list[ImportParkingSpotException] = []

        # Karlsruhes http-server config misses the intermediate cert GeoTrust TLS RSA CA G1, so we add it here manually.
        ca_path = Path(Path(__file__).parent, 'files', 'ca.crt.pem')
        response = self.request_get(url=self.source_info.source_url, verify=str(ca_path), timeout=30)
        response_data = response.json()

        try:
            realtime_input: GeojsonInput = self.geojson_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

        for update_dict in realtime_input.features:
            try:
                karlsruhe_input = self.geojson_feature_validator.validate(update_dict)
                static_parking_spot_inputs += karlsruhe_input.to_static_parking_spot_inputs()
            except ValidationError as e:
                import_parking_spot_exceptions.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=update_dict.get('properties', {}).get('id'),
                        message=f'Invalid data at uid {update_dict.get("properties", {}).get("id")}: '
                        f'{e.to_dict()}, data: {update_dict}',
                    ),
                )
                continue

        return self.apply_static_patches(static_parking_spot_inputs), import_parking_spot_exceptions
