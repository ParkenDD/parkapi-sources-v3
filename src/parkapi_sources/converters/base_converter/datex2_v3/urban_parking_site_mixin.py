"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from lxml import etree
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.datex2 import Datex2StaticMixin
from parkapi_sources.util import XMLHelper

from .urban_parking_site_validator import UrbanParkingSite


class UrbanParkingSiteV3Mixin(Datex2StaticMixin, ABC):
    """
    Static data of DATEX II v3 parking table publications with urban parking sites.
    """

    xml_helper: XMLHelper
    static_validator = DataclassValidator(UrbanParkingSite)
    datex2_root_element = 'payload'

    def _transform_static_xml_to_static_input_dicts(self, xml_data: etree.Element) -> list[dict]:
        data = self.xml_helper.xml_to_dict(
            xml_data,
            conditional_remote_type_tags=[
                ('parkingName', 'values'),
                ('parkingDescription', 'values'),
                ('contactOrganisationName', 'values'),
                ('values', 'value'),
            ],
            ensure_array_keys=[
                ('payload', 'parkingTable'),
                ('parkingTable', 'parkingRecord'),
                ('parkingRecord', 'parkingAccess'),
                ('parkingRecord', 'groupOfParkingSpaces'),
                ('parkingRecord', 'parkingUsageScenario'),
                ('onlyAssignedParking', 'applicableForUser'),
            ],
        )
        parking_records: list[dict] = []
        for parking_table in data.get('payload', {}).get('parkingTable', []):
            parking_records += parking_table.get('parkingRecord', [])

        return parking_records

    def get_uid_from_static_input_dict(self, input_dict: dict) -> str:
        return input_dict.get('id')
