"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import csv
from io import StringIO

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import BielefeldParkingSiteInput


class BielefeldPullConverter(ParkingSitePullConverter):
    bielefeld_parking_site_validator = DataclassValidator(BielefeldParkingSiteInput)

    source_info = SourceInfo(
        uid='bielefeld',
        name='Stadt Bielefeld',
        public_url='https://www.bielefeld.de/node/3035',
        source_url=(
            'https://www.bielefeld01.de/md/WFS/parkplaetze/01?SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature'
            '&TYPENAME=parkplaetze_p&SRSNAME=EPSG:4326&OUTPUTFORMAT=text/csv'
            '&NW_INFO=/parkplaetze_p_EPSG25832_CSV.csv'
        ),
        has_realtime_data=False,
        attribution_license='CC BY 4.0',
        attribution_contributor='Stadt Bielefeld',
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        response = self.request_get(url=self.source_info.source_url, timeout=30)
        reader = csv.DictReader(StringIO(response.text), delimiter=';')

        for row in reader:
            parking_site_dict = {key: (value if value != '' else None) for key, value in row.items()}

            # Rename WKT to wkt for validataclass
            if 'WKT' in parking_site_dict:
                parking_site_dict['wkt'] = parking_site_dict.pop('WKT')

            try:
                parking_site_input = self.bielefeld_parking_site_validator.validate(parking_site_dict)
                static_parking_site_inputs.append(parking_site_input.to_static_parking_site())
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('gid'),
                        message=f'validation error for data {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return self.apply_static_patches(static_parking_site_inputs), static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []
