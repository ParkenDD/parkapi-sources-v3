"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import csv
from io import StringIO

import pyproj
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.push import CsvConverter
from parkapi_sources.converters.reutlingen_bike.validation import ReutlingenBikeRowInput
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput


class ReutlingenBikePushConverter(CsvConverter):
    proj: pyproj.Proj = pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True)
    reutlingen_bike_row_validator = DataclassValidator(ReutlingenBikeRowInput)

    source_info = SourceInfo(
        uid='reutlingen_bike',
        name='Stadt Reutlingen: Fahrrad-Abstellanlagen',
        public_url='https://www.reutlingen.de',
        has_realtime_data=False,
    )

    header_mapping: dict[str, str] = {
        '\ufeffSTANDORT': 'name',
        'ANZAHL': 'capacity',
        'ANLAGE': 'additional_name',
        'GEOM': 'coordinates',
    }

    def handle_csv_string(
        self,
        data: StringIO,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return self.handle_csv(list(csv.reader(data, dialect='unix', delimiter=',')))

    def handle_csv(self, data: list[list]) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        mapping: dict[str, int] = self.get_mapping_by_header(self.header_mapping, data[0])

        # We start at row 2, as the first one is our header
        for row in data[1:]:
            input_dict: dict[str, str] = {}
            for field in self.header_mapping.values():
                input_dict[field] = row[mapping[field]]

            try:
                reutlingen_bike_row_input: ReutlingenBikeRowInput = self.reutlingen_bike_row_validator.validate(
                    input_dict,
                )
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('name'),
                        message=f'validation error for {input_dict}: {e.to_dict()}',
                    ),
                )
                continue

            static_parking_site_inputs.append(reutlingen_bike_row_input.to_parking_site_input(self.proj))

        return static_parking_site_inputs, static_parking_site_errors
