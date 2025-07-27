"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import ParkingSpotBaseConverter
from parkapi_sources.converters.base_converter.push import CsvConverter
from parkapi_sources.converters.reutlingen_disabled.validation import ReutlingenDisabledRowInput
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSpotInput


class ReutlingenDisabledPushConverter(CsvConverter, ParkingSpotBaseConverter):
    reutlingen_disabled_row_validator = DataclassValidator(ReutlingenDisabledRowInput)

    source_info = SourceInfo(
        uid='reutlingen_disabled',
        name='Stadt Reutlingen: Behindertenparkplätze',
        public_url='https://www.reutlingen.de',
        has_realtime_data=False,
    )

    header_mapping: dict[str, str] = {
        '\ufeffid': 'uid',
        'ort': 'name',
        'GEOM': 'coordinates',
    }

    def handle_csv(self, data: list[list]) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSiteException]]:
        static_data_updated_at = datetime.now(tz=timezone.utc)
        static_parking_spot_inputs: list[StaticParkingSpotInput] = []
        static_parking_spot_errors: list[ImportParkingSiteException] = []

        mapping: dict[str, int] = self.get_mapping_by_header(self.header_mapping, data[0])

        # We start at row 2, as the first one is our header
        for row in data[1:]:
            input_dict: dict[str, str] = {}
            for field in self.header_mapping.values():
                input_dict[field] = row[mapping[field]]

            try:
                reutlingen_disabled_row_input: ReutlingenDisabledRowInput = (
                    self.reutlingen_disabled_row_validator.validate(
                        input_dict,
                    )
                )
            except ValidationError as e:
                static_parking_spot_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=input_dict.get('uid'),
                        message=f'validation error for {input_dict}: {e.to_dict()}',
                    ),
                )
                continue

            static_parking_spot_inputs.append(
                reutlingen_disabled_row_input.to_parking_spot_input(
                    static_data_updated_at=static_data_updated_at,
                ),
            )

        return static_parking_spot_inputs, static_parking_spot_errors
