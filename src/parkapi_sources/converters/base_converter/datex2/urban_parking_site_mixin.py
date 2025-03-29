"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from lxml import etree
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.datex2 import Datex2StaticMixin
from parkapi_sources.util import XMLHelper

from .urban_parking_site_validator import UrbanParkingSite


class UrbanParkingSiteMixin(Datex2StaticMixin, ABC):
    xml_helper: XMLHelper
    static_validator = DataclassValidator(UrbanParkingSite)

    def _transform_static_xml_to_static_input_dicts(self, xml_data: etree.Element) -> list[dict]:
        data = self.xml_helper.xml_to_dict(
            xml_data,
            conditional_remote_type_tags=[
                ('parkingName', 'values'),
                ('values', 'value'),
            ],
            ensure_array_keys=[
                ('parkingTable', 'parkingRecord'),
                ('parkingName', 'values'),
                ('assignedParkingAmongOthers', 'applicableForUser'),
            ],
        )
        return (
            data.get('d2LogicalModel', {})
            .get('payloadPublication', {})
            .get('genericPublicationExtension', {})
            .get('parkingTablePublication', {})
            .get('parkingTable', {})
            .get('parkingRecord', [])
        )

    def get_uid_from_static_input_dict(self, input_dict: dict) -> str:
        return input_dict.get('id')
