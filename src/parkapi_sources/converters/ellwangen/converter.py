"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

from openpyxl.cell import Cell

from parkapi_sources.converters.base_converter.push import NormalizedXlsxConverter
from parkapi_sources.models import SourceInfo


class EllwangenPushConverter(NormalizedXlsxConverter):
    source_info = SourceInfo(
        uid='ellwangen',
        name='Ellwangen Parkdaten',
        public_url='https://www.ellwangen.de',
        has_realtime_data=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For some reason, Ellwangen decided to change the titles
        ellwangen_header_rows: dict[str, str] = {
            'Maximale Parkdauer / min': 'max_stay',
            'Anzahl Frauen-parkplätze': 'capacity_woman',
            'Anzahl Behinderten-parkplätze': 'capacity_disabled',
            'Anlage beleuchtet': 'has_lighting',
            'gebührenpflichtig': 'has_fee',
            'Anzahl Stellplätze': 'capacity',
            'Anzahl Carsharing-Parkplätze': 'capacity_carsharing',
            'Existieren Live-Daten': 'has_realtime_data',
            '24/7 geöffnet': 'opening_hours_is_24_7',
        }
        self.header_row = {
            **{key: value for key, value in super().header_row.items() if value not in ellwangen_header_rows.values()},
            **ellwangen_header_rows,
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
        parking_site_dict['max_stay'] = parking_site_dict['max_stay'] * 60 if parking_site_dict['max_stay'] else None
        parking_site_dict['type'] = self.type_mapping.get(parking_site_dict.get('type'))
        parking_site_dict['static_data_updated_at'] = datetime.now(tz=timezone.utc).isoformat()

        return parking_site_dict
