"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

from openpyxl.cell import Cell

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.push import NormalizedXlsxConverter
from parkapi_sources.models import SourceInfo


class BBParkhausPushConverter(NormalizedXlsxConverter, ParkingSiteBaseConverter):
    source_info = SourceInfo(
        uid='bb_parkhaus',
        name='B+B Parkhaus GmbH & Co. KG',
        public_url='https://www.bb-parkhaus.de',
        has_realtime_data=False,
    )

    purpose_mapping: dict[str, str] = {
        'Auto': 'CAR',
        'Fahrrad': 'BIKE',
    }

    supervision_type_mapping: dict[bool, str] = {
        True: 'YES',
        False: 'NO',
    }

    boolean_type_mapping: dict[str, bool] = {
        'true': True,
        'false': False,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For some reason, BB Parkhaus decided to change the titles
        bb_parkhaus_header_rows: dict[str, str] = {
            'Zweck der Anlage': 'purpose',
            'Ladeplätze': 'capacity_charging',
            'Gebührenpflichtig?': 'has_fee',
            'is_covered': 'is_covered',
            'is_supervised': 'supervision_type',
        }
        self.header_row = {
            **{
                key: value for key, value in super().header_row.items() if value not in bb_parkhaus_header_rows.values()
            },
            **bb_parkhaus_header_rows,
        }

    def map_row_to_parking_site_dict(
        self,
        mapping: dict[str, int],
        row: tuple[Cell, ...],
        **kwargs: Any,
    ) -> dict[str, Any]:
        parking_site_dict = super().map_row_to_parking_site_dict(mapping, row, **kwargs)

        for field in mapping.keys():
            parking_site_dict[field] = row[mapping[field]].value

        parking_site_dict['opening_hours'] = parking_site_dict['opening_hours'].replace('00:00-00:00', '00:00-24:00')
        parking_site_dict['type'] = self.type_mapping.get(parking_site_dict.get('type'))
        parking_site_dict['purpose'] = self.purpose_mapping.get(parking_site_dict.get('purpose'))
        parking_site_dict['fee_description'] = ' '.join(
            parking_site_dict.get('fee_description', '').strip().splitlines()
        )
        parking_site_dict['supervision_type'] = self.supervision_type_mapping.get(
            self.boolean_type_mapping.get(parking_site_dict.get('supervision_type')),
        )
        parking_site_dict['is_covered'] = self.boolean_type_mapping.get(parking_site_dict.get('is_covered'))
        parking_site_dict['static_data_updated_at'] = datetime.now(tz=timezone.utc).isoformat()

        return parking_site_dict
