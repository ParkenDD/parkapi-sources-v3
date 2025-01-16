"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

from openpyxl.cell import Cell

from parkapi_sources.converters.base_converter.push import NormalizedXlsxConverter
from parkapi_sources.models import SourceInfo


class GoldbeckPushConverter(NormalizedXlsxConverter):
    source_info = SourceInfo(
        uid='goldbeck',
        name='GOLDBECK Parking Services GmbH',
        public_url='https://www.goldbeck-parking.de',
        has_realtime_data=False,
    )

    purpose_mapping: dict[str, str] = {
        'Auto': 'CAR',
        'Fahrrad': 'BIKE',
    }

    supervision_type_mapping: dict[str, str] = {
        True: 'YES',
        False: 'NO',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For some reason, Goldbeck decided to change the titles
        goldbeck_header_rows: dict[str, str] = {
            'Einfahrtshöhe (cm)': 'max_height',
            'Zweck der Anlage': 'purpose',
            'Überdachung': 'is_covered',
            'Art der Überwachung': 'supervision_type',
        }
        self.header_row = {
            **{key: value for key, value in super().header_row.items() if value not in goldbeck_header_rows.values()},
            **goldbeck_header_rows,
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
        parking_site_dict['purpose'] = self.purpose_mapping.get(parking_site_dict.get('purpose'))
        parking_site_dict['type'] = self.type_mapping.get(parking_site_dict.get('type'), 'OFF_STREET_PARKING_GROUND')
        parking_site_dict['supervision_type'] = self.supervision_type_mapping.get(
            parking_site_dict.get('supervision_type'),
        )
        parking_site_dict['static_data_updated_at'] = datetime.now(tz=timezone.utc).isoformat()

        return parking_site_dict
