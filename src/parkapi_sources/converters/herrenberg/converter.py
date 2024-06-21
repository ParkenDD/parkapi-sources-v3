"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import requests
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import BaseConverter
from parkapi_sources.converters.herrenberg.mapper import Herrenbergmapper
from parkapi_sources.converters.herrenberg.validation import HerrenbergParkingSiteInput
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import StaticParkingSiteInput, SourceInfo, RealtimeParkingSiteInput


class HerrenbergPullConverter(BaseConverter):
    mapper = Herrenbergmapper()
    _base_url = 'https://api.stadtnavi.de/herrenberg/parking/parkapi.json'
    parking_site_validator = DataclassValidator(HerrenbergParkingSiteInput)

    source_info = SourceInfo(
        uid='herrenberg',
        name='Stadt Herrenberg',
        public_url='https://www.herrenberg.de/de/Stadtleben/Erlebnis-Herrenberg/Service/Parkplaetze',
        source_url='/home/jebus/Arbeit/parkapi-sources-v3-t/tests/converters/data/herrenberg.json',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Herrenberg',
        has_realtime_data=False,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        input_data = self._get_remote_data()

        for item in input_data:
            try:
                validated: HerrenbergParkingSiteInput = self.parking_site_validator.validate(item)
            except ValidationError as e:
                try:
                    static_parking_site_errors.append(
                        ImportParkingSiteException(
                            source_uid=self.source_info.uid,
                            parking_site_uid=item.id,
                            message=f'validation error: {e.to_dict()}',
                        ),
                    )
                except AttributeError:
                    static_parking_site_errors.append(
                        ImportParkingSiteException(
                            source_uid=self.source_info.uid,
                            parking_site_uid=None,
                            message=f'validation error: {e.to_dict()}',
                        ),
                    )
                    continue
            static_parking_site_inputs.append(self.mapper.map_static_parking_site(validated))
        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []
        # since there is no realtimedata this is just skipped

    def _get_remote_data(self) -> list[dict]:
        response = requests.get(self._base_url, timeout=60)
        result_dict: dict = response.json()

        items: list[dict] = []
        for item in result_dict['lots']:
            if item['lot_type'] == 'Barrierefreier-Parkplatz':
                item['total'] = item.pop('total:disabled')
            items.append(item)
        return items
