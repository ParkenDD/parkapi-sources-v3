"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from lxml import etree
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.aachen.validators import ParkingRecord
from parkapi_sources.converters.base_converter.datex2 import Datex2StaticMixin, ParkingRecordStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekPullConverter
from parkapi_sources.models import SourceInfo


class AachenPullConverter(Datex2StaticMixin, ParkingRecordStatusMixin, MobilithekPullConverter):
    config_key = 'AACHEN'
    static_validator = DataclassValidator(ParkingRecord)

    source_info = SourceInfo(
        uid='aachen',
        name='Aachen',
        public_url='https://mobilithek.info/offers/110000000003300000',
        has_realtime_data=True,
    )

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
