"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

import requests
from lxml import etree
from validataclass.exceptions import ValidationError

from parkapi_sources.converters.base_converter.pull import Datex2Mixin, PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkAndRideType
from parkapi_sources.util import XMLHelper


class VrsBasePullConverter(PullConverter, Datex2Mixin, ABC):
    xml_helper = XMLHelper()

    @property
    @abstractmethod
    def config_key(self) -> str:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_config_keys = [
            'PARK_API_VRS_CERT',
            'PARK_API_VRS_KEY',
            f'PARK_API_VRS_{self.config_key}_STATIC_SUBSCRIPTION_ID',
            f'PARK_API_VRS_{self.config_key}_REALTIME_SUBSCRIPTION_ID',
        ]

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        datex2_parking_facilities = self._get_xml_data_as_dict(
            subscription_id=self.config_helper.get(f'PARK_API_VRS_{self.config_key}_STATIC_SUBSCRIPTION_ID'),
        )

        static_parking_site_inputs, static_parking_site_errors = self._handle_datex2_parking_facilities(
            datex2_parking_facilities,
        )
        for static_parking_site_input in static_parking_site_inputs:
            static_parking_site_input.park_and_ride_type = [ParkAndRideType.YES]
            static_parking_site_input.opening_hours = '24/7'

        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[[list[RealtimeParkingSiteInput]], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        realtime_parking_site_errors: list[ImportParkingSiteException] = []

        datex2_parking_facilities = self._get_xml_data_as_dict(
            subscription_id=self.config_helper.get(f'PARK_API_VRS_{self.config_key}_REALTIME_SUBSCRIPTION_ID'),
        )

        parking_record_status_list = datex2_parking_facilities.get('parkingStatusPublication', {}).get(
            'parkingRecordStatus', []
        )

        for parking_record_status in parking_record_status_list:
            try:
                realtime_parking_site_inputs.append(self._handle_parking_record_status(parking_record_status))
            except ValidationError as e:
                realtime_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_record_status.get('parkingRecordReference', {}).get('id'),
                        message=str(e.to_dict()),
                    ),
                )

        return realtime_parking_site_inputs, realtime_parking_site_errors

    def _get_xml_data_as_dict(self, subscription_id: int) -> dict:
        url = (
            f'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/{subscription_id}'
            f'/clientPullService?subscriptionID={subscription_id}'
        )
        response = requests.get(
            url,
            timeout=30,
            cert=(self.config_helper.get('PARK_API_VRS_CERT'), self.config_helper.get('PARK_API_VRS_KEY')),
        )

        root = etree.fromstring(response.text, parser=etree.XMLParser(resolve_entities=False))  # noqa: S320

        data = self.xml_helper.xml_to_dict(
            root,
            conditional_remote_type_tags=[
                ('values', 'value'),
                ('parkingFacilityName', 'values'),
            ],
            ensure_array_keys=[
                ('parkingFacilityTable', 'parkingFacility'),
                ('parkingFacility', 'assignedParkingSpaces'),
                ('parkingStatusPublication', 'parkingRecordStatus'),
            ],
        )
        return data.get('d2LogicalModel', {}).get('payloadPublication', {}).get('genericPublicationExtension', {})

    def _handle_parking_record_status(self, parking_record_status_data: dict) -> RealtimeParkingSiteInput:
        parking_occupancy_data = parking_record_status_data.get('parkingOccupancy')
        input_data = {
            'uid': parking_record_status_data.get('parkingRecordReference', {}).get('id', ''),
            'realtime_capacity': int(parking_occupancy_data.get('parkingNumberOfSpacesOverride', 0)),
            'realtime_free_capacity': int(parking_occupancy_data.get('parkingNumberOfVacantSpaces', 0)),
            'realtime_data_updated_at': parking_record_status_data.get('parkingStatusOriginTime'),
        }

        # Some converters add the name after the uid (like: `12345[Name]`). Let's remove the name.
        input_data['uid'] = input_data['uid'].split('[')[0]

        return self.realtime_parking_site_validator.validate(input_data)


class VrsBondorfPullConverter(VrsBasePullConverter):
    config_key = 'BONDORF'

    source_info = SourceInfo(
        uid='vrs_bondorf',
        name='Verband Region Stuttgart: Bondorf',
        public_url='https://mobilithek.info',
        source_url='https://mobilithek.info',
        attribution_contributor='Verband Region Stuttgart',
        attribution_license='Datenlizenz Deutschland – Namensnennung – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/by-2-0',
        has_realtime_data=True,
    )


class VrsKirchheimPullConverter(VrsBasePullConverter):
    config_key = 'KIRCHHEIM'

    source_info = SourceInfo(
        uid='vrs_kirchheim',
        name='Verband Region Stuttgart: Kirchheim',
        public_url='https://mobilithek.info',
        source_url='https://mobilithek.info',
        attribution_contributor='Verband Region Stuttgart',
        attribution_license='Datenlizenz Deutschland – Namensnennung – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/by-2-0',
        has_realtime_data=True,
    )


class VrsNeustadtPullConverter(VrsBasePullConverter):
    config_key = 'NEUSTADT'

    source_info = SourceInfo(
        uid='vrs_neustadt',
        name='Verband Region Stuttgart: Neustadt',
        public_url='https://mobilithek.info',
        source_url='https://mobilithek.info',
        attribution_contributor='Verband Region Stuttgart',
        attribution_license='Datenlizenz Deutschland – Namensnennung – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/by-2-0',
        has_realtime_data=True,
    )


class VrsVaihingenPullConverter(VrsBasePullConverter):
    config_key = 'VAIHINGEN'

    source_info = SourceInfo(
        uid='vrs_vaihingen',
        name='Verband Region Stuttgart: Vaihingen',
        public_url='https://mobilithek.info',
        source_url='https://mobilithek.info',
        attribution_contributor='Verband Region Stuttgart',
        attribution_license='Datenlizenz Deutschland – Namensnennung – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/by-2-0',
        has_realtime_data=True,
    )
