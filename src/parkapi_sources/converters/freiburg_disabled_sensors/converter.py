"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSpotPullConverter
from parkapi_sources.exceptions import ImportParkingSpotException, ImportSourceException
from parkapi_sources.models import GeojsonInput, RealtimeParkingSpotInput, SourceInfo, StaticParkingSpotInput

from .models import FreiburgDisabledSensorFeatureInput


class FreiburgDisabledSensorsPullConverter(ParkingSpotPullConverter):
    geojson_validator = DataclassValidator(GeojsonInput)
    geojson_feature_validator = DataclassValidator(FreiburgDisabledSensorFeatureInput)

    source_info = SourceInfo(
        uid='freiburg_disabled_sensors',
        name='Stadt Freiburg',
        source_url='https://geoportal.freiburg.de/wfs/gdm_parkpl/gdm_parkpl?SERVICE=WFS&REQUEST=GetFeature'
        '&SRSNAME=EPSG:4326&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=beh_parkpl_ueberw&OUTPUTFORMAT=geojson',
        has_realtime_data=True,
    )

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[StaticParkingSpotInput] = []

        freiburg_inputs, import_parking_spot_exceptions = self._get_raw_parking_spots()

        for freiburg_input in freiburg_inputs:
            static_parking_spot_inputs.append(freiburg_input.to_static_parking_spot_input())

        return self.apply_static_patches(static_parking_spot_inputs), import_parking_spot_exceptions

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        realtime_parking_spot_inputs: list[RealtimeParkingSpotInput] = []

        freiburg_inputs, import_parking_spot_exceptions = self._get_raw_parking_spots()

        for freiburg_input in freiburg_inputs:
            realtime_parking_spot_inputs.append(freiburg_input.to_realtime_parking_spot_input())

        return realtime_parking_spot_inputs, import_parking_spot_exceptions

    def _get_raw_parking_spots(
        self,
    ) -> tuple[list[FreiburgDisabledSensorFeatureInput], list[ImportParkingSpotException]]:
        freiburg_inputs: list[FreiburgDisabledSensorFeatureInput] = []
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
                freiburg_inputs.append(self.geojson_feature_validator.validate(update_dict))
            except ValidationError as e:
                import_parking_spot_exceptions.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=update_dict.get('properties', {}).get('name'),
                        message=f'Invalid data at uid {update_dict.get("properties", {}).get("name")}: '
                        f'{e.to_dict()}, data: {update_dict}',
                    ),
                )
                continue

        return freiburg_inputs, import_parking_spot_exceptions
