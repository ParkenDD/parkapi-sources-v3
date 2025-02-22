"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.converters.herrenberg.models import (
    HerrenbergParkingSiteInput,
    HerrenbergParkingSitesInput,
    HerrenbergState,
)
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput


class HerrenbergPullConverter(PullConverter):
    parking_sites_input_validator = DataclassValidator(HerrenbergParkingSitesInput)
    parking_site_validator = DataclassValidator(HerrenbergParkingSiteInput)

    source_info = SourceInfo(
        uid='herrenberg',
        name='Stadt Herrenberg',
        public_url='https://www.herrenberg.de/de/Stadtleben/Erlebnis-Herrenberg/Service/Parkplaetze',
        source_url='https://api.stadtnavi.de/herrenberg/parking/parkapi.json',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Herrenberg',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        parking_site_inputs, parking_site_errors, last_updated = self._get_parking_site_inputs()

        for parking_site_input in parking_site_inputs:
            static_parking_site_inputs.append(parking_site_input.to_static_parking_site(last_updated))

        return static_parking_site_inputs, parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        parking_site_inputs, parking_site_errors, last_updated = self._get_parking_site_inputs()

        for parking_site_input in parking_site_inputs:
            if parking_site_input.state == HerrenbergState.NODATA:
                continue
            realtime_parking_site_inputs.append(parking_site_input.to_realtime_parking_site(last_updated))

        return realtime_parking_site_inputs, parking_site_errors

    def _get_parking_site_inputs(
        self,
    ) -> tuple[list[HerrenbergParkingSiteInput], list[ImportParkingSiteException], datetime]:
        parking_site_inputs: list[HerrenbergParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        response = self.request_get(url=self.source_info.source_url, timeout=60)
        parking_sites_input: HerrenbergParkingSitesInput = self.parking_sites_input_validator.validate(response.json())

        for parking_site_dict in parking_sites_input.lots:
            # replace : by _ in order to use validataclass directly
            for key in list(parking_site_dict.keys()):
                if ':' in key:
                    parking_site_dict[key.replace(':', '_')] = parking_site_dict.pop(key)

            try:
                parking_site_inputs.append(self.parking_site_validator.validate(parking_site_dict))
            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('id'),
                        message=f'validation error for static data {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return parking_site_inputs, parking_site_errors, parking_sites_input.last_updated
