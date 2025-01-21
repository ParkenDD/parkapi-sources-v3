"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import PurposeType

from .validators import (
    BahnParkingSiteCapacityType,
    BahnParkingSiteInput,
)


class BahnMapper:
    def map_static_parking_site_car(self, bahn_input: BahnParkingSiteInput) -> StaticParkingSiteInput | None:
        return self._map_static_parking_site(
            bahn_input,
            '-parking',
            PurposeType.CAR,
            BahnParkingSiteCapacityType.PARKING,
        )

    def map_static_parking_site_bike_locked(self, bahn_input: BahnParkingSiteInput) -> StaticParkingSiteInput | None:
        return self._map_static_parking_site(
            bahn_input,
            '-bike-locked',
            PurposeType.BIKE,
            BahnParkingSiteCapacityType.BIKE_PARKING_LOCKED,
        )

    def map_static_parking_site_bike_open(self, bahn_input: BahnParkingSiteInput) -> StaticParkingSiteInput | None:
        return self._map_static_parking_site(
            bahn_input,
            '-bike-open',
            PurposeType.BIKE,
            BahnParkingSiteCapacityType.BIKE_PARKING_OPEN,
        )

    @staticmethod
    def _map_static_parking_site(
        bahn_input: BahnParkingSiteInput,
        uid_suffix: str,
        purpose: PurposeType,
        capacity_type: BahnParkingSiteCapacityType,
    ) -> StaticParkingSiteInput | None:
        capacity_input = bahn_input.get_capacity_by_type(capacity_type)
        if capacity_input is None:
            return None

        if capacity_type == BahnParkingSiteCapacityType.PARKING:
            parking_site_type = bahn_input.type.name.to_parking_site_type_input()
        else:
            parking_site_type = capacity_input.to_bike_parking_site_type_input()

        static_parking_site_input = StaticParkingSiteInput(
            uid=f'{bahn_input.id}{uid_suffix}',
            group_uid=str(bahn_input.id),
            name=bahn_input.get_name(),
            lat=bahn_input.address.location.latitude,
            lon=bahn_input.address.location.longitude,
            operator_name=bahn_input.operator.name,
            address=f'{bahn_input.address.streetAndNumber}, {bahn_input.address.zip} {bahn_input.address.city}',
            type=parking_site_type,
            has_realtime_data=False,  # TODO: change this as soon as Bahn offers proper rate limits
            static_data_updated_at=datetime.now(tz=timezone.utc),
            public_url=bahn_input.url,
            purpose=purpose,
            capacity=capacity_input.total,
        )
        if bahn_input.access.openingHours.is24h:
            static_parking_site_input.opening_hours = '24/7'

        # Map all additional capacities
        if capacity_type == BahnParkingSiteCapacityType.PARKING:
            for capacity_data in bahn_input.capacity:
                if capacity_data.type == BahnParkingSiteCapacityType.HANDICAPPED_PARKING:
                    static_parking_site_input.capacity_disabled = capacity_data.total

        return static_parking_site_input
