"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

from openpyxl.cell import Cell

from parkapi_sources.converters.base_converter.push import NormalizedXlsxConverter
from parkapi_sources.models import SourceInfo


class HuefnerPushConverter(NormalizedXlsxConverter):
    source_info = SourceInfo(
        uid='huefner',
        name='PARK SERVICE HÜFNER GmbH & Co. KG',
        public_url='https://www.ps-huefner.de/parken.php',
        has_realtime_data=False,
    )

    purpose_mapping: dict[str, str] = {
        'Auto': 'CAR',
        'Fahrrad': 'BIKE',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For new required ParkAPI field "purpose"
        self.header_row = {
            **super().header_row,
            'Zweck der Anlage': 'purpose',
        }

    def map_row_to_parking_site_dict(
        self,
        mapping: dict[str, int],
        row: tuple[Cell, ...],
        **kwargs: Any,
    ) -> dict[str, Any]:
        parking_site_dict = super().map_row_to_parking_site_dict(mapping, row, **kwargs)
        if '-00:00' in parking_site_dict['opening_hours']:
            parking_site_dict['opening_hours'] = parking_site_dict['opening_hours'].replace('-00:00', '-24:00')

        parking_site_dict['purpose'] = self.purpose_mapping.get(parking_site_dict.get('purpose'))
        parking_site_dict['static_data_updated_at'] = datetime.now(tz=timezone.utc).isoformat()

        return parking_site_dict
