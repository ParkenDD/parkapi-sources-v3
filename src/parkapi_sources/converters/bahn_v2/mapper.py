"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from parkapi_sources.models import StaticParkingSiteInput

from .validators import (
    BahnBikeLockedParkingSiteInput,
    BahnBikeOpenParkingSiteInput,
    BahnParkingSiteCapacityType,
    BahnParkingSiteInput,
    NameContext,
)


class BahnMapper:
    @staticmethod
    def map_static_parking_site(bahn_input: BahnParkingSiteInput) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            uid=f'{bahn_input.id}-parking',
            group_uid=str(bahn_input.id),
            name=next(
                iter(name_input.name for name_input in bahn_input.name if name_input.context == NameContext.NAME)
            ),
            lat=bahn_input.address.location.latitude,
            lon=bahn_input.address.location.longitude,
            operator_name=bahn_input.operator.name,
            address=f'{bahn_input.address.streetAndNumber}, {bahn_input.address.zip} {bahn_input.address.city}',
            type=bahn_input.type.name.to_parking_site_type_input(),
            has_realtime_data=False,  # TODO: change this as soon as Bahn offers proper rate limits
            static_data_updated_at=datetime.now(tz=timezone.utc),
            public_url=bahn_input.url,
            purpose=next(
                iter(
                    item.to_purpose_type_input()
                    for item in bahn_input.capacity
                    if item.type == BahnParkingSiteCapacityType.PARKING
                )
            ),
            # Because it was checked in validation, we can be sure that capacity will be set
            capacity=next(
                iter(
                    int(round(item.total))
                    for item in bahn_input.capacity
                    if item.type == BahnParkingSiteCapacityType.PARKING
                )
            ),
        )
        if bahn_input.access.openingHours.is24h:
            static_parking_site_input.opening_hours = '24/7'

        # Map all additional capacities
        for capacity_data in bahn_input.capacity:
            if capacity_data.type == BahnParkingSiteCapacityType.HANDICAPPED_PARKING:
                static_parking_site_input.capacity_disabled = int(round(capacity_data.total))

        return static_parking_site_input


class BahnBikeParkingLockedMapper:
    @staticmethod
    def map_static_parking_site(bahn_input: BahnBikeLockedParkingSiteInput) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            uid=f'{bahn_input.id}-bike-locked',
            group_uid=str(bahn_input.id),
            name=next(
                iter(name_input.name for name_input in bahn_input.name if name_input.context == NameContext.NAME)
            ),
            lat=bahn_input.address.location.latitude,
            lon=bahn_input.address.location.longitude,
            operator_name=bahn_input.operator.name,
            address=f'{bahn_input.address.streetAndNumber}, {bahn_input.address.zip} {bahn_input.address.city}',
            type=next(
                iter(
                    item.to_bike_parking_site_type_input()
                    for item in bahn_input.capacity
                    if item.type == BahnParkingSiteCapacityType.BIKE_PARKING_LOCKED
                )
            ),
            has_realtime_data=False,  # TODO: change this as soon as Bahn offers proper rate limits
            static_data_updated_at=datetime.now(tz=timezone.utc),
            public_url=bahn_input.url,
            purpose=next(
                iter(
                    item.to_purpose_type_input()
                    for item in bahn_input.capacity
                    if item.type == BahnParkingSiteCapacityType.BIKE_PARKING_LOCKED
                )
            ),
            # Because it was checked in validation, we can be sure that capacity will be set
            capacity=sum(
                iter(
                    int(round(item.total))
                    for item in bahn_input.capacity
                    if item.type in [BahnParkingSiteCapacityType.BIKE_PARKING_LOCKED]
                )
            ),
        )
        if bahn_input.access.openingHours.is24h:
            static_parking_site_input.opening_hours = '24/7'

        return static_parking_site_input


class BahnBikeParkingOpenMapper:
    @staticmethod
    def map_static_parking_site(bahn_input: BahnBikeOpenParkingSiteInput) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            uid=f'{bahn_input.id}-bike-open',
            group_uid=str(bahn_input.id),
            name=next(
                iter(name_input.name for name_input in bahn_input.name if name_input.context == NameContext.NAME)
            ),
            lat=bahn_input.address.location.latitude,
            lon=bahn_input.address.location.longitude,
            operator_name=bahn_input.operator.name,
            address=f'{bahn_input.address.streetAndNumber}, {bahn_input.address.zip} {bahn_input.address.city}',
            type=next(
                iter(
                    item.to_bike_parking_site_type_input()
                    for item in bahn_input.capacity
                    if item.type == BahnParkingSiteCapacityType.BIKE_PARKING_OPEN
                )
            ),
            has_realtime_data=False,  # TODO: change this as soon as Bahn offers proper rate limits
            static_data_updated_at=datetime.now(tz=timezone.utc),
            public_url=bahn_input.url,
            purpose=next(
                iter(
                    item.to_purpose_type_input()
                    for item in bahn_input.capacity
                    if item.type == BahnParkingSiteCapacityType.BIKE_PARKING_OPEN
                )
            ),
            # Because it was checked in validation, we can be sure that capacity will be set
            capacity=sum(
                iter(
                    int(round(item.total))
                    for item in bahn_input.capacity
                    if item.type in [BahnParkingSiteCapacityType.BIKE_PARKING_OPEN]
                )
            ),
        )
        if bahn_input.access.openingHours.is24h:
            static_parking_site_input.opening_hours = '24/7'

        return static_parking_site_input
