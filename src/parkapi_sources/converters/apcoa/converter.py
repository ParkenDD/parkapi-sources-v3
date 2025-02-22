"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    SourceInfo,
    StaticParkingSiteInput,
)

from .mapper import ApcoaMapper
from .validators import ApcoaParkingSiteInput, ApcoaParkingSitesInput


class ApcoaPullConverter(PullConverter):
    required_config_keys = ['PARK_API_APCOA_API_SUBSCRIPTION_KEY']

    mapper = ApcoaMapper()
    apcoa_parking_sites_validator = DataclassValidator(ApcoaParkingSitesInput)
    apcoa_parking_site_validator = DataclassValidator(ApcoaParkingSiteInput)

    source_info = SourceInfo(
        uid='apcoa',
        name='APCOA-SERVICES API',
        public_url='https://devzone.apcoa-services.com/',
        source_url='https://api.apcoa-services.com/carpark/v4/Carparks',
        has_realtime_data=False,  # ATM only static data can be called from the API
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        parking_sites_input = self.get_data()

        for parking_site_dict in parking_sites_input.Results:
            # Ignore Park & Control Objects/Entries - Not allowed to be published
            if (
                parking_site_dict.get('SiteIdLong').startswith('S1180_')
                and parking_site_dict.get('ShowAs') == 'SURVEILLANCE_OBJECT'
            ):
                continue

            # Ignore missing coordinates if requested
            if self.config_helper.get('PARK_API_APCOA_IGNORE_MISSING_COORDINATES', False):
                if not parking_site_dict.get('NavigationLocations'):
                    continue

            try:
                parking_site_input: ApcoaParkingSiteInput = self.apcoa_parking_site_validator.validate(
                    parking_site_dict,
                )
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('CarParkId'),
                        message=f'validation error for data {parking_site_dict}: {e.to_dict()}',
                    ),
                )
                continue

            static_parking_site_inputs.append(self.mapper.map_static_parking_site(parking_site_input))
        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []  # ATM only static data can be called from the API

    def get_data(self) -> ApcoaParkingSitesInput:
        headers: dict[str, str] = {
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': self.config_helper.get('PARK_API_APCOA_API_SUBSCRIPTION_KEY'),
        }

        response = self.request_get(
            url=self.source_info.source_url,
            headers=headers,
            timeout=60,
        )
        return self.apcoa_parking_sites_validator.validate(response.json())
