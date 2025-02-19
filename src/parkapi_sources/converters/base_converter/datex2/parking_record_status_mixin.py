"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from lxml import etree
from validataclass.validators import DataclassValidator

from parkapi_sources.util import XMLHelper

from .datex2_realtime_mixin import Datex2RealtimeMixin
from .parking_record_status_validator import ParkingRecordStatus


class ParkingRecordStatusMixin(Datex2RealtimeMixin, ABC):
    xml_helper: XMLHelper
    realtime_validator = DataclassValidator(ParkingRecordStatus)

    def _transform_realtime_xml_to_realtime_input_dicts(self, xml_data: etree.Element) -> list[dict]:
        data = self.xml_helper.xml_to_dict(
            xml_data,
            ensure_array_keys=[
                ('parkingStatusPublication', 'parkingRecordStatus'),
            ],
        )
        return (
            data.get('d2LogicalModel', {})
            .get('payloadPublication', {})
            .get('genericPublicationExtension', {})
            .get('parkingStatusPublication', {})
            .get('parkingRecordStatus', [])
        )

    def get_uid_from_realtime_input_dict(self, input_dict: dict) -> str:
        return input_dict.get('id')
