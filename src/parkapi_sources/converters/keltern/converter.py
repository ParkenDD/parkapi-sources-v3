"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from openpyxl import Workbook
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.push import XlsxConverter
from parkapi_sources.converters.keltern.validator import KelternRowInput
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput


class KelternPushConverter(XlsxConverter, ParkingSiteBaseConverter):
    keltern_row_validator = DataclassValidator(KelternRowInput)

    source_info = SourceInfo(
        uid='keltern',
        name='Gemeinde Keltern',
        public_url='https://www.keltern.de/startseite',
        has_realtime_data=False,
    )

    def handle_xlsx(self, workbook: Workbook) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        worksheet = workbook.active
        fields = next(worksheet.rows)

        # We start at row 2, as the first one is our header
        for row in worksheet.iter_rows(min_row=2):
            # ignore empty lines as LibreOffice sometimes adds empty rows at the end of a file
            if row[0].value is None:
                continue

            parking_site_raw_dict: dict[str, str] = {}
            for i, field in enumerate(fields):
                parking_site_raw_dict[field.value] = row[i].value

            try:
                keltern_row_input = self.keltern_row_validator.validate(parking_site_raw_dict)
                static_parking_site_inputs.append(keltern_row_input.to_static_parking_site_input())

            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_raw_dict.get('id'),
                        message=f'invalid static parking site data {parking_site_raw_dict}: {e.to_dict()}',
                    )
                )
                continue

        return static_parking_site_inputs, static_parking_site_errors
