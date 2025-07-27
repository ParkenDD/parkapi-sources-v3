"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from datetime import datetime, timezone
from typing import Any

from openpyxl.cell import Cell
from openpyxl.workbook.workbook import Workbook
from validataclass.exceptions import ValidationError

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.push import XlsxConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput


class PumBwPushConverter(XlsxConverter, ParkingSiteBaseConverter):
    source_info = SourceInfo(
        uid='pum_bw',
        name='Baden-Württemberg: Parken und Mitfahren',
        public_url='https://mobidata-bw.de/dataset/p-m-parkplatze-baden-wurttemberg',
        has_realtime_data=False,
    )

    header_row: dict[str, str] = {
        'Id': 'uid',
        'Bezeichnung': 'name',
        'BAB/B': 'autobahn',
        'Nr': 'autobahn_no',
        'Breite': 'lat',
        'Länge': 'lon',
        'Anbindung über(Str.Nr. Bundes- oder Landesstraße)': 'description',
        'Anzahl der Pkw-Parkstände': 'capacity',
        'Beleuchtung(vorhanden / nicht vorhanden)': 'has_lighting',
        'Google Maps': 'public_url',
    }

    boolean_mapping: dict[str, bool] = {
        'vorhanden': True,
        'nicht vorhanden': False,
        'Durchfahrt beleuchtet': True,
        'teilweise beleuchtet': True,
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
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('uid'),
                        message=f'invalid static parking site data: {e.to_dict()}',
                    )
                )
                continue

        return static_parking_site_inputs, static_parking_site_errors

    def map_row_to_parking_site_dict(self, mapping: dict[str, int], row: list[Cell]) -> dict[str, Any]:
        parking_site_dict: dict[str, Any] = {}
        for field in mapping.keys():
            parking_site_dict[field] = row[mapping[field]].value

        parking_site_dict['name'] = f'{parking_site_dict["name"]}'
        if parking_site_dict['autobahn'] and parking_site_dict['autobahn_no']:
            parking_site_dict['name'] = (
                f'{parking_site_dict["autobahn"]}{parking_site_dict["autobahn_no"]} {parking_site_dict["name"]}'
            )

        parking_site_dict['type'] = 'OFF_STREET_PARKING_GROUND'
        parking_site_dict['park_and_ride_type'] = ['CARPOOL']
        parking_site_dict['static_data_updated_at'] = datetime.now(tz=timezone.utc).isoformat()
        parking_site_dict['capacity'] = int(parking_site_dict['capacity'])
        parking_site_dict['has_lighting'] = self.boolean_mapping.get(parking_site_dict['has_lighting'].rstrip(), None)
        parking_site_dict['has_realtime_data'] = False

        # Since the URL to Google map is in Excel Hyperlink, then we format it to url string for public_url
        if '=HYPERLINK' in parking_site_dict['public_url']:
            url_input = parking_site_dict['public_url']
            url_input = (
                url_input[: url_input.find('q=') + 2]
                + f'{parking_site_dict["lat"]},{parking_site_dict["lon"]}'
                + url_input[url_input.find('&ie') :]
            )
            public_url_match = re.search(r'(https[^")]+)', url_input)
            parking_site_dict['public_url'] = public_url_match.group(0) if public_url_match else None

        return parking_site_dict
