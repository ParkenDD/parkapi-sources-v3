"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from lxml import etree
from validataclass.validators import DataclassValidator

from parkapi_sources.util import XMLHelper

from .datex2_static_mixin import Datex2StaticMixin
from .parking_facility_validator import ParkingFacility


class ParkingFacilityMixin(Datex2StaticMixin, ABC):
    xml_helper: XMLHelper
    static_validator = DataclassValidator(ParkingFacility)

    def _transform_static_xml_to_static_input_dicts(self, xml_data: etree.Element) -> list[dict]:
        data = self.xml_helper.xml_to_dict(
            xml_data,
            conditional_remote_type_tags=[
                ('values', 'value'),
                ('parkingFacilityName', 'values'),
                ('periodName', 'values'),
                ('openingTimes', 'period'),
            ],
            ensure_array_keys=[
                ('parkingFacilityTable', 'parkingFacility'),
                ('parkingFacility', 'assignedParkingSpaces'),
            ],
        )
        return (
            data.get('d2LogicalModel', {})
            .get('payloadPublication', {})
            .get('genericPublicationExtension', {})
            .get('parkingFacilityTablePublication', {})
            .get('parkingFacilityTable', {})
            .get('parkingFacility', [])
        )

    def get_uid_from_static_input_dict(self, input_dict: dict) -> str:
        return input_dict.get('id')
