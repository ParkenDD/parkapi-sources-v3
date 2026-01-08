"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSpotPullConverter
from parkapi_sources.exceptions import ImportParkingSpotException, ImportSourceException
from parkapi_sources.models import GeojsonInput, RealtimeParkingSpotInput, SourceInfo, StaticParkingSpotInput

from .models import KarlsruheDisabledFeatureInput, KarlsruheDisabledRealtimeInput, KarlsruheDisabledRealtimeItemInput


class KarlsruheDisabledPullConverter(ParkingSpotPullConverter):
    geojson_validator = DataclassValidator(GeojsonInput)
    geojson_feature_validator = DataclassValidator(KarlsruheDisabledFeatureInput)
    realtime_validator = DataclassValidator(KarlsruheDisabledRealtimeInput)
    realtime_item_validator = DataclassValidator(KarlsruheDisabledRealtimeItemInput)

    source_info = SourceInfo(
        uid='karlsruhe_disabled',
        name='Stadt Karlsruhe: Behindertenparkplätze',
        source_url='https://mobil.trk.de/geoserver/TBA/ows?service=WFS&version=1.0.0&request=GetFeature'
        '&srsname=EPSG:4326&typeName=TBA%3Abehinderten_parkplaetze&outputFormat=application%2Fjson',
        has_realtime_data=True,
    )

    realtime_source_url = (
        'https://mobil.trk.de/swkiot/tags/c9ac643f-aedd-4794-83fb-7b7337744480/devices?limit=99&last_readings=1'
        '&auth={auth}'
    )

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[StaticParkingSpotInput] = []
        import_parking_spot_exceptions: list[ImportParkingSpotException] = []

        features_data = self._get_static_data()

        for update_dict in features_data.features:
            try:
                karlsruhe_input: KarlsruheDisabledFeatureInput = self.geojson_feature_validator.validate(update_dict)
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

    def _get_static_data(self) -> GeojsonInput:
        # Karlsruhes http-server config misses the intermediate cert GeoTrust TLS RSA CA G1, so we add it here manually.
        ca_path = Path(Path(__file__).parent, 'files', 'ca.crt.pem')
        response = self.request_get(url=self.source_info.source_url, verify=str(ca_path), timeout=30)
        response_data = response.json()

        try:
            return self.geojson_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        if (auth := self.config_helper.get('PARK_API_KARLSRUHE_DISABLED_AUTH')) is None:
            return [], []
        features_data = self._get_static_data()

        sensors_by_uid: dict[str, str] = {}
        for update_dict in features_data.features:
            try:
                karlsruhe_input: KarlsruheDisabledFeatureInput = self.geojson_feature_validator.validate(update_dict)
            except ValidationError:
                # No error handling here, as we just need it for mapping purposes
                continue
            if karlsruhe_input.properties.sensorenliste is None:
                continue
            for i, sensor_uid in enumerate(karlsruhe_input.properties.sensorenliste):
                sensors_by_uid[sensor_uid] = f'{karlsruhe_input.properties.id}_{i}'

        response = self.request_get(url=self.realtime_source_url.format(auth=auth))
        try:
            realtime_body: KarlsruheDisabledRealtimeInput = self.realtime_validator.validate(response.json())
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid input at source {self.source_info.uid}: {e.to_dict()}, data: {response.content.decode()}',
            ) from e

        realtime_parking_spot_inputs: list[RealtimeParkingSpotInput] = []
        import_parking_spot_exceptions: list[ImportParkingSpotException] = []
        for realtime_dict in realtime_body.body:
            try:
                realtime_item: KarlsruheDisabledRealtimeItemInput = self.realtime_item_validator.validate(realtime_dict)
                if realtime_item.id not in sensors_by_uid:
                    continue
                realtime_parking_spot_inputs.append(
                    realtime_item.to_realtime_parking_spot_input(
                        sensors_by_uid[realtime_item.id],
                    ),
                )
            except ValidationError as e:
                import_parking_spot_exceptions.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=realtime_dict.get('id'),
                        message=f'Invalid data at uid {realtime_dict.get("id")}: {e.to_dict()}, data: {realtime_dict}',
                    ),
                )
                continue

        return realtime_parking_spot_inputs, import_parking_spot_exceptions
