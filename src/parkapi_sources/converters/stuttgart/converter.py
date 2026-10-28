"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pyproj
from lxml.etree import Element
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingFacilityMixin, ParkingFacilityStatusMixin
from parkapi_sources.converters.base_converter.push import XmlConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput
from parkapi_sources.util import round_7d

from .validators import StuttgartParkingFacility


class StuttgartPushConverter(ParkingFacilityMixin, ParkingFacilityStatusMixin, XmlConverter, ParkingSiteBaseConverter):
    proj: pyproj.Proj = pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True)
    static_validator = DataclassValidator(StuttgartParkingFacility)

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
        static_parking_site_input.lat = round_7d(coordinates[1])
        static_parking_site_input.lon = round_7d(coordinates[0])

    def handle_xml(
        self,
        root: Element,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        path_prefix = (
            '/*[name()="d2LogicalModel"]/*[name()="payloadPublication"]/*[name()="genericPublicationExtension"]'
        )

        if len(root.xpath(f'{path_prefix}/*[name()="parkingFacilityTablePublication"]/*')):
            return self.handle_static_xml_data(static_xml_data=root)
        if len(root.xpath(f'{path_prefix}/*[name()="parkingFacilityTableStatusPublication"]/*')):
            return self.handle_realtime_xml_data(realtime_xml_data=root)

        # There's no known XML format
        raise ImportSourceException(
            source_uid=self.source_info.uid,
            message='Unknown XML data structure',
        )
