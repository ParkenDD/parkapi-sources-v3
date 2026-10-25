"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from lxml import etree
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.datex2 import Datex2RealtimeMixin
from parkapi_sources.util import XMLHelper

from .parking_record_status_validator import ParkingRecordStatus


class ParkingRecordStatusV3Mixin(Datex2RealtimeMixin, ABC):
    """
    Realtime data of DATEX II v3 parking status publications.
    """

    xml_helper: XMLHelper
    realtime_validator = DataclassValidator(ParkingRecordStatus)
    datex2_root_element = 'payload'

    def _transform_realtime_xml_to_realtime_input_dicts(self, xml_data: etree.Element) -> list[dict]:
        data = self.xml_helper.xml_to_dict(
            xml_data,
            ensure_array_keys=[
                ('payload', 'parkingRecordStatus'),
            ],
        )
        return [
            parking_record_status
            for parking_record_status in data.get('payload', {}).get('parkingRecordStatus', [])
            # A parking record status with a validity offset to its origin time is a forecast, not the current status
            if 'parkingStatusValidity' not in parking_record_status
        ]

    def get_uid_from_realtime_input_dict(self, input_dict: dict) -> str:
        return input_dict.get('parkingRecordReference', {}).get('id')
