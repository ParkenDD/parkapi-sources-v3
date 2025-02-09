"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import ROUND_HALF_UP, Decimal

import pyproj
from lxml import etree
from lxml.etree import Element
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.datex2 import Datex2RealtimeMixin, ParkingFacilityMixin
from parkapi_sources.converters.base_converter.push import XmlConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .validators import ParkingFacilityStatus, StuttgartParkingFacility


class StuttgartPushConverter(ParkingFacilityMixin, Datex2RealtimeMixin, XmlConverter):
    proj: pyproj.Proj = pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True)
    static_validator = DataclassValidator(StuttgartParkingFacility)
    realtime_validator = DataclassValidator(ParkingFacilityStatus)

    source_info = SourceInfo(
        uid='stuttgart',
        name='Stadt Stuttgart',
        attribution_contributor='Landeshauptstadt Stuttgart, Tiefbauamt',
        attribution_license='dl-de/by-2-0',
        has_realtime_data=True,
    )

    def modify_static_parking_site_input(self, static_parking_site_input: StaticParkingSiteInput):
        coordinates = self.proj(
            float(static_parking_site_input.lon),
            float(static_parking_site_input.lat),
            inverse=True,
        )
        static_parking_site_input.lat = Decimal(coordinates[1]).quantize(Decimal('1.0000000'), rounding=ROUND_HALF_UP)
        static_parking_site_input.lon = Decimal(coordinates[0]).quantize(Decimal('1.0000000'), rounding=ROUND_HALF_UP)

    def handle_xml(
        self,
        root: Element,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        path_prefix = (
            '/*[name()="d2LogicalModel"]/*[name()="payloadPublication"]/*[name()="genericPublicationExtension"]'
        )

        if len(root.xpath(f'{path_prefix}/*[name()="parkingFacilityTablePublication"]/*')):
            return self._handle_static_xml_data(static_xml_data=root)
        if len(root.xpath(f'{path_prefix}/*[name()="parkingFacilityTableStatusPublication"]/*')):
            return self._handle_realtime_xml_data(realtime_xml_data=root)

        # There's no known XML format
        raise ImportSourceException(
            source_uid=self.source_info.uid,
            message='Unknown XML data structure',
        )

    def _transform_realtime_xml_to_realtime_input_dicts(self, realtime_xml_data: etree.Element) -> list[dict]:
        data = self.xml_helper.xml_to_dict(
            realtime_xml_data,
            ensure_array_keys=[
                ('parkingFacilityTableStatusPublication', 'parkingFacilityStatus'),
                ('parkingFacilityStatus', 'parkingFacilityStatus'),
            ],
        )
        return (
            data.get('d2LogicalModel', {})
            .get('payloadPublication', {})
            .get('genericPublicationExtension', {})
            .get('parkingFacilityTableStatusPublication', {})
            .get('parkingFacilityStatus', [])
        )

    def get_uid_from_realtime_input_dict(self, input_dict: dict) -> str:
        return input_dict.get('parkingFacilityReference', {}).get('id')
