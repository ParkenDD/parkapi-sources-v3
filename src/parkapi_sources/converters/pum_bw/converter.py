"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

from openpyxl.cell import Cell
from openpyxl.workbook.workbook import Workbook
from validataclass.exceptions import ValidationError

from parkapi_sources.converters.base_converter.push import XlsxConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput


class PumBwPushConverter(XlsxConverter):
    source_info = SourceInfo(
        uid='pum_bw',
        name='Baden-Württemberg: Parken und Mitfahren',
        public_url='https://mobidata-bw.de/dataset/p-m-parkplatze-baden-wurttemberg',
        has_realtime_data=False,
    )

    header_row: dict[str, str] = {
        'AS-Nummer': 'uid',
        'Bezeichnung Parkplatz': 'name',
        'Straße': 'street',
        'Längengrad': 'lat',
        'Breitengrad': 'lon',
        'Zufahrt': 'description',
        'Anzahl Plätze': 'capacity',
    }

    def handle_xlsx(self, workbook: Workbook) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        worksheet = workbook.active
        mapping: dict[str, int] = self.get_mapping_by_header(next(worksheet.rows))

        # We start at row 2, as the first one is our header
        for row in worksheet.iter_rows(min_row=2):
            # ignore empty lines as LibreOffice sometimes adds empty rows at the end of a file
            if row[0].value is None:
                continue
            parking_site_dict = self.map_row_to_parking_site_dict(mapping, row)

            try:
                static_parking_site_inputs.append(self.static_parking_site_validator.validate(parking_site_dict))
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        uid=parking_site_dict.get('uid'),
                        message=f'invalid static parking site data: {e.to_dict()}',
                    )
                )
                continue

        return static_parking_site_inputs, static_parking_site_errors

    @staticmethod
    def map_row_to_parking_site_dict(mapping: dict[str, int], row: list[Cell]) -> dict[str, Any]:
        parking_site_dict: dict[str, Any] = {}
        for field in mapping.keys():
            parking_site_dict[field] = row[mapping[field]].value

        parking_site_dict['uid'] = f'{parking_site_dict["uid"]}-{parking_site_dict["name"]}'
        parking_site_dict['name'] = f'{parking_site_dict["street"]} {parking_site_dict["name"]}'
        parking_site_dict['type'] = 'OFF_STREET_PARKING_GROUND'
        parking_site_dict['park_and_ride_type'] = ['CARPOOL']
        parking_site_dict['static_data_updated_at'] = datetime.now(tz=timezone.utc).isoformat()

        return parking_site_dict
