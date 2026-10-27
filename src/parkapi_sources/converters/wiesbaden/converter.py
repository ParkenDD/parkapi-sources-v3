"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingRecordStatusMixin, UrbanParkingSiteMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo


class WiesbadenPullConverter(
    UrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The static data is not valid DATEX II: the opening times use times like 00:00 instead of 00:00:00.
    """

    config_key = 'WIESBADEN'

    source_info = SourceInfo(
        uid='wiesbaden',
        name='Landeshauptstadt Wiesbaden',
        public_url='https://mobilithek.info/offers/110000000003166000',
        attribution_contributor='Landeshauptstadt Wiesbaden',
        has_realtime_data=True,
    )

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        # The realtime data just contains the number of occupied spaces, so we fetch the static data as well to
        # calculate the free capacity with the static capacity.
        static_parking_site_inputs, _ = self.get_static_parking_sites()
        capacity_by_uid: dict[str, int] = {
            static_parking_site_input.uid: static_parking_site_input.capacity
            for static_parking_site_input in static_parking_site_inputs
        }

        realtime_xml_data = self._get_xml_data(
            subscription_id=self.config_helper.get(f'PARK_API_MOBILITHEK_{self.config_key}_REALTIME_SUBSCRIPTION_ID'),
        )

        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        realtime_parking_site_errors: list[ImportParkingSiteException] = []

        for realtime_input_dict in self._transform_realtime_xml_to_realtime_input_dicts(realtime_xml_data):
            try:
                realtime_item = self.realtime_validator.validate(realtime_input_dict)
                realtime_parking_site_inputs.append(
                    realtime_item.to_realtime_parking_site_input(
                        static_capacity=capacity_by_uid.get(realtime_item.uid),
                    ),
                )
            except ValidationError as e:
                realtime_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=self.get_uid_from_realtime_input_dict(realtime_input_dict),
                        message=str(e.to_dict()),
                    ),
                )

        return realtime_parking_site_inputs, realtime_parking_site_errors
