"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pyproj
from lxml.etree import Element
from validataclass.exceptions import ValidationError

from parkapi_sources.converters.base_converter.pull import Datex2Mixin
from parkapi_sources.converters.base_converter.push import XmlConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput


class StuttgartPushConverter(XmlConverter, Datex2Mixin):
    proj: pyproj.Proj = pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True)

    source_info = SourceInfo(
        uid='stuttgart',
        name='Stadt Stuttgart',
        public_url='https://service.mdm-portal.de/mdm-portal-application/publDetail.do?publicationId=3059002',
        attribution_contributor='Landeshauptstadt Stuttgart, Tiefbauamt',
        attribution_license='dl-de/by-2-0',
        has_realtime_data=True,
    )

    def handle_xml(
        self,
        root: Element,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        data = self.xml_helper.xml_to_dict(
            root,
            conditional_remote_type_tags=[
                ('values', 'value'),
                ('periodName', 'values'),
                ('parkingFacilityName', 'values'),
                ('openingTimes', 'period'),
            ],
            ensure_array_keys=[
                ('parkingFacilityTable', 'parkingFacility'),
                ('parkingFacility', 'assignedParkingSpaces'),
                ('parkingFacilityTableStatusPublication', 'parkingFacilityStatus'),
            ],
        )
        items_base = data.get('d2LogicalModel', {}).get('payloadPublication', {}).get('genericPublicationExtension', {})
        if items_base.get('parkingFacilityTablePublication'):
            return self._handle_datex2_parking_facilities(items_base)

        if items_base.get('parkingFacilityTableStatusPublication'):
            realtime_items = items_base.get('parkingFacilityTableStatusPublication', {}).get(
                'parkingFacilityStatus', []
            )
            realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
            realtime_parking_site_errors: list[ImportParkingSiteException] = []

            for realtime_item in realtime_items:
                try:
                    realtime_parking_site_inputs.append(self._handle_realtime_item(realtime_item))
                except ValidationError as e:
                    realtime_parking_site_errors.append(
                        ImportParkingSiteException(
                            source_uid=self.source_info.uid,
                            parking_site_uid=realtime_item.get('parkingFacilityReference', {}).get('id'),
                            message=str(e.to_dict()),
                        ),
                    )

            return realtime_parking_site_inputs, realtime_parking_site_errors

        return [], []

    def _handle_realtime_item(self, item: dict) -> RealtimeParkingSiteInput:
        input_data = {
            'uid': item.get('parkingFacilityReference', {}).get('id'),
            'realtime_free_capacity': int(item.get('totalNumberOfVacantParkingSpaces', 0)),
            'realtime_data_updated_at': item.get('parkingFacilityStatusTime'),
        }

        status_list: list[str] = item.get('parkingFacilityStatus', [])
        if 'open' in status_list:
            input_data['realtime_opening_status'] = 'open'
        elif 'closed' in status_list:
            input_data['realtime_opening_status'] = 'closed'

        return self.realtime_parking_site_validator.validate(input_data)
