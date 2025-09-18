"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSpotPullConverter
from parkapi_sources.exceptions import ImportParkingSpotException, ImportSourceException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSpotInput

from .models import KonstanzDisabledFeatureInput


class KonstanzDisabledPullConverter(ParkingSpotPullConverter):
    geojson_validator = DataclassValidator(GeojsonInput)
    geojson_feature_validator = DataclassValidator(KonstanzDisabledFeatureInput)

    source_info = SourceInfo(
        uid='konstanz_disabled',
        name='Stadt Konstanz: Behindertenparkplätze',
        source_url='https://services-eu1.arcgis.com/cgMeYTGtzFtnxdsx/arcgis/rest/services/POI_Verkehr/FeatureServer'
        '/5/query?outFields=*&where=1%3D1&f=geojson',
        has_realtime_data=False,
    )

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[StaticParkingSpotInput] = []
        import_parking_spot_exceptions: list[ImportParkingSpotException] = []

        response = self.request_get(url=self.source_info.source_url, timeout=30)
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
                konstanz_input = self.geojson_feature_validator.validate(update_dict)
                static_parking_spot_inputs += konstanz_input.to_static_parking_spot_inputs()
            except ValidationError as e:
                import_parking_spot_exceptions.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=update_dict.get('properties', {}).get('GlobalID'),
                        message=f'Invalid data at uid {update_dict.get("properties", {}).get("GlobalID")}: '
                        f'{e.to_dict()}, data: {update_dict}',
                    ),
                )
                continue

        return self.apply_static_patches(static_parking_spot_inputs), import_parking_spot_exceptions
