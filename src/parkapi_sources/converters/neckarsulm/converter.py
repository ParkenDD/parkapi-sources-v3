"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.push import CsvConverter
from parkapi_sources.converters.neckarsulm.models import NeckarsulmRowInput
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput


class NeckarsulmPushConverter(CsvConverter):
    neckarsulm_row_validator = DataclassValidator(NeckarsulmRowInput)

    source_info = SourceInfo(
        uid='neckarsulm',
        name='Stadt Neckarsulm: PKW-Parkplätze',
        public_url='https://www.neckarsulm.de',
        has_realtime_data=False,
    )

    header_mapping: dict[str, str] = {
        'id': 'uid',
        'name': 'name',
        'kategorie': 'type',
        'y-koord': 'lat',
        'x-koord': 'lon',
        'strasse': 'street',
        'plz': 'postcode',
        'stadt': 'city',
        'anz_plaetze': 'capacity',
        'anzcarsharing': 'capacity_carsharing',
        'anzeladestation': 'capacity_charging',
        'anzfrauenpark': 'capacity_woman',
        'anzbehinderte': 'capacity_disabled',
        'gebuehren': 'has_fee',
        'open_time': 'opening_hours',
        'maxhoehe': 'max_height',
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
                input_data: NeckarsulmRowInput = self.neckarsulm_row_validator.validate(input_dict)
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
