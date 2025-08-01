"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

import pyproj
from openpyxl.cell import Cell

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.push import NormalizedXlsxConverter
from parkapi_sources.models import SourceInfo
from parkapi_sources.models.enums import ParkAndRideType, PurposeType


class VrsParkAndRidePushConverter(NormalizedXlsxConverter, ParkingSiteBaseConverter):
    proj: pyproj.Proj = pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True)

    source_info = SourceInfo(
        uid='vrs-p-r',
        name='Verband Region Stuttgart: Park and Ride',
        public_url='https://www.region-stuttgart.org/de/bereiche-aufgaben/mobilitaet/park-ride/',
        has_realtime_data=False,
    )

    # If there are more tables with our defined format, it would make sense to move header_row to XlsxConverter
    header_row: dict[str, str] = {
        'AnlagenNr': 'uid',
        'AnlageNamen': 'name',
        'Art_der_Anlage': 'type',
        'BetreiberName': 'operator_name',
        'POINT_X': 'lon_utm',
        'POINT_Y': 'lat_utm',
        'Anzahl_Stellplätze_gesamt': 'capacity',
        'Anzahl_Carsharing_Stellplätze': 'capacity_carsharing',
        'Anzahl_E_Ladestationen': 'capacity_charging',
        'Anzahl_Behindertenparkplätze': 'capacity_disabled',
        'Gebühren': 'has_fee',
        'Durchgehend_geöffnet': 'opening_hours_is_24_7',
        # Maximale_Parkdauer is there, but is not parsable
        # Other opening times are there, but not parsable
    }

    def map_row_to_parking_site_dict(
        self,
        mapping: dict[str, int],
        row: tuple[Cell, ...],
        column_names: list[str],
    ) -> dict[str, Any]:
        parking_site_dict = super().map_row_to_parking_site_dict(mapping, row, column_names)

        if 'Zufahrt' in column_names:
            if row[column_names.index('Zufahrt')].value == 'offen' or (
                row[column_names.index('Zufahrt')].value == 'beschrankt'
                and row[column_names.index('Durchgehend_geöffnet')].value == 'ja'
            ):
                parking_site_dict['opening_hours'] = '24/7'

        for field in mapping.keys():
            parking_site_dict[field] = row[mapping[field]].value

        coordinates = self.proj(
            float(parking_site_dict.get('lon_utm')),
            float(parking_site_dict.get('lat_utm')),
            inverse=True,
        )
        parking_site_dict['lat'] = coordinates[1]
        parking_site_dict['lon'] = coordinates[0]

        parking_site_dict['opening_hours'] = parking_site_dict['opening_hours'].replace('-00:00', '-24:00')
        parking_site_dict['purpose'] = PurposeType.CAR.name
        parking_site_dict['park_and_ride_type'] = [ParkAndRideType.TRAIN.name]
        parking_site_dict['type'] = self.type_mapping.get(parking_site_dict.get('type'))
        parking_site_dict['static_data_updated_at'] = datetime.now(tz=timezone.utc).isoformat()
        parking_site_dict['has_realtime_data'] = False

        return parking_site_dict
