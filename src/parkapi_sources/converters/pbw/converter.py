"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .mapper import PbwMapper
from .validation import PbwCityInput, PbwParkingSiteDetailInput, PbwParkingSiteInput, PbwRealtimeInput


class PbwPullConverter(PullConverter):
    _base_url = 'https://www.mypbw.de/api/'
    required_config_keys = ['PARK_API_PBW_API_KEY']

    mapper = PbwMapper()

    city_validator = DataclassValidator(PbwCityInput)
    parking_site_detail_validator = DataclassValidator(PbwParkingSiteDetailInput)
    parking_site_validator = DataclassValidator(PbwParkingSiteInput)
    realtime_validator = DataclassValidator(PbwRealtimeInput)

    source_info = SourceInfo(
        uid='pbw',
        name='Parkraumgesellschaft Baden-Württemberg',
        public_url='https://www.pbw.de',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        city_dicts = self._get_remote_data('catalog-city')
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        for city_dict in city_dicts:
            try:
                city_input: PbwCityInput = self.city_validator.validate(city_dict)
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=city_dict.get('id'),
                        message=f'validation error: {e.to_dict()}',
                    ),
                )
                continue

            parking_site_detail_dicts = self._get_remote_data('object-by-city', city_input.id)

            for parking_site_detail_dict in parking_site_detail_dicts:
                try:
                    parking_site_detail_input: PbwParkingSiteDetailInput = self.parking_site_detail_validator.validate(
                        parking_site_detail_dict
                    )
                except ValidationError as e:
                    static_parking_site_errors.append(
                        ImportParkingSiteException(
                            source_uid=self.source_info.uid,
                            parking_site_uid=str(city_input.id),
                            message=f'validation error at data {parking_site_detail_dict}: {e.to_dict()}',
                        ),
                    )
                    continue

                static_parking_site_inputs.append(
                    self.mapper.map_static_parking_site(parking_site_detail_input),
                )

        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        realtime_parking_site_errors: list[ImportParkingSiteException] = []

        realtime_dicts = self._get_remote_data('object-dynamic-all')

        for realtime_dict in realtime_dicts:
            try:
                realtime_input: PbwRealtimeInput = self.realtime_validator.validate(realtime_dict)
                realtime_parking_site_inputs.append(self.mapper.map_realtime_parking_site(realtime_input))
            except ValidationError as e:
                realtime_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=realtime_dict.get('id'),
                        message=f'validation error at data {realtime_dict}: {e.to_dict()}',
                    )
                )

        return realtime_parking_site_inputs, realtime_parking_site_errors

    def _get_remote_data(self, data_type: str, data_id: Optional[int] = None) -> list[dict]:
        parameters = {
            'format': 'json',
            'key': self.config_helper.get('PARK_API_PBW_API_KEY'),
            'type': data_type,
        }
        if data_id is not None:
            parameters['id'] = data_id

        response = self.request_get(url=self._base_url, params=parameters, timeout=60)
        result_dict: dict = response.json()

        items: list[dict] = []
        for key, item in result_dict.items():
            item['id'] = key
            items.append(item)

        return items
