"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from lxml import etree
from validataclass.validators import DataclassValidator

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput
from parkapi_sources.util import XMLHelper

from .datex2_realtime_mixin import Datex2RealtimeMixin
from .parking_facility_status_validator import ParkingFacilityStatus


class ParkingFacilityStatusMixin(Datex2RealtimeMixin, ABC):
    xml_helper: XMLHelper
    realtime_validator = DataclassValidator(ParkingFacilityStatus)

    def _transform_realtime_xml_to_realtime_input_dicts(self, xml_data: etree.Element) -> list[dict]:
        data = self.xml_helper.xml_to_dict(
            xml_data,
            ensure_array_keys=[
                ('parkingFacilityTableStatusPublication', 'parkingFacilityStatus'),
                ('parkingFacilityStatus', 'parkingFacilityStatus'),
            ],
        )
        return (
            data
            .get('d2LogicalModel', {})
            .get('payloadPublication', {})
            .get('genericPublicationExtension', {})
            .get('parkingFacilityTableStatusPublication', {})
            .get('parkingFacilityStatus', [])
        )

    def get_uid_from_realtime_input_dict(self, input_dict: dict) -> str:
        return input_dict.get('parkingFacilityReference', {}).get('id')

    def _handle_realtime_xml_data(
        self,
        realtime_xml_data: etree.Element,
    ) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs, realtime_parking_site_errors = super()._handle_realtime_xml_data(
            realtime_xml_data,
        )

        # Some sources publish a separate status per capacity type (e.g. short term and long term) for the same
        # parking facility. These partial states add up to the state of the parking facility.
        merged_realtime_parking_site_inputs: dict[str, RealtimeParkingSiteInput] = {}
        for realtime_parking_site_input in realtime_parking_site_inputs:
            existing_input = merged_realtime_parking_site_inputs.get(realtime_parking_site_input.uid)
            if existing_input is None:
                merged_realtime_parking_site_inputs[realtime_parking_site_input.uid] = realtime_parking_site_input
                continue
            existing_input.realtime_capacity = self._add_optional(
                existing_input.realtime_capacity,
                realtime_parking_site_input.realtime_capacity,
            )
            existing_input.realtime_free_capacity = self._add_optional(
                existing_input.realtime_free_capacity,
                realtime_parking_site_input.realtime_free_capacity,
            )
            existing_input.realtime_data_updated_at = max(
                existing_input.realtime_data_updated_at,
                realtime_parking_site_input.realtime_data_updated_at,
            )

        return list(merged_realtime_parking_site_inputs.values()), realtime_parking_site_errors

    @staticmethod
    def _add_optional(first: int | None, second: int | None) -> int | None:
        # If one of the partial values is unknown, the sum is unknown, too
        if first is None or second is None:
            return None
        return first + second
