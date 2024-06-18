"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.push import CsvConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput

from .models import KonstanzRowInput


class KonstanzBikePushConverter(CsvConverter):
    konstanz_bike_row_validator = DataclassValidator(KonstanzRowInput)
    csv_delimiter = ','

    source_info = SourceInfo(
        uid='konstanz_bike',
        name='Stadt Konstanz: Fahrrad-Abstellanlagen',
        public_url='https://www.konstanz.de/',
        has_realtime_data=False,
    )

    header_mapping: dict[str, str] = {
        'ABSTELL_NR': 'uid',
        'Lagebezeichnung': 'address',
        'Art': 'type',
        'Ueberdachung': 'is_covered',
        'Beleuchtung': 'has_lighting',
        'Eigentuemer_Baulasttraeger': 'operator_name',
        'Stadtteil': 'district',
        'Kapazitaet': 'capacity',
        'coordinates': 'coordinates',
        'geometry': 'geometry',
    }

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
                input_data: KonstanzRowInput = self.konstanz_bike_row_validator.validate(input_dict)
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('id'),
                        message=f'validation error for {input_dict}: {e.to_dict()}',
                    ),
                )
                continue

            static_parking_site_inputs.append(input_data.to_static_parking_site_input())

        return static_parking_site_inputs, static_parking_site_errors
