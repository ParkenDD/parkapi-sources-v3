"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from zoneinfo import ZoneInfo

from validataclass.dataclasses import validataclass
from validataclass.validators import (
    AnythingValidator,
    DataclassValidator,
    DateTimeValidator,
    DecimalValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType


class FacilityLayout(Enum):
    SINGLE_LEVEL = 'singleLevel'

    def to_parking_site_type(self) -> ParkingSiteType | None:
        return {
            self.SINGLE_LEVEL: ParkingSiteType.CAR_PARK,
        }.get(self)


@validataclass
class InnerAssignedParkingSpace:
    descriptionOfAssignedParkingSpaces: dict = AnythingValidator(allowed_types=dict)
    numberOfAssignedParkingSpaces: int = IntegerValidator(allow_strings=True)

    def get_sub_capacity(self) -> str | None:
        if self.descriptionOfAssignedParkingSpaces == {'personTypeForWhichSpacesAssigned': 'women'}:
            return 'capacity_woman'
        if self.descriptionOfAssignedParkingSpaces == {'personTypeForWhichSpacesAssigned': 'families'}:
            return 'capacity_family'
        if self.descriptionOfAssignedParkingSpaces == {'personTypeForWhichSpacesAssigned': 'disabled'}:
            return 'capacity_disabled'
        if self.descriptionOfAssignedParkingSpaces == {
            'characteristicsOfVehiclesForWhichSpacesAssigned': {'fuelType': 'battery'}
        }:
            return 'capacity_charging'
        return None


@validataclass
class OuterAssignedParkingSpace:
    assignedParkingSpaces: InnerAssignedParkingSpace = DataclassValidator(InnerAssignedParkingSpace)


@validataclass
class LocationForDisplay:
    latitude: Decimal = DecimalValidator(min_value=40, max_value=60)
    longitude: Decimal = DecimalValidator(min_value=7, max_value=10)


@validataclass
class FacilityLocation:
    locationForDisplay: LocationForDisplay = DataclassValidator(LocationForDisplay)


@validataclass
class Owner:
    contactName: str | None = Noneable(StringValidator())


@validataclass
class ParkingFacility:
    assignedParkingSpaces: list[OuterAssignedParkingSpace] = ListValidator(
        DataclassValidator(OuterAssignedParkingSpace),
    )
    facilityLocation: FacilityLocation = DataclassValidator(FacilityLocation)
    id: str = StringValidator()
    owner: Owner = DataclassValidator(Owner)
    parkingFacilityLayout: FacilityLayout = EnumValidator(FacilityLayout)
    parkingFacilityName: str = StringValidator()
    parkingFacilityRecordVersionTime: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    totalParkingCapacity: int = IntegerValidator(allow_strings=True)
    totalParkingCapacityLongTerm: int = IntegerValidator(allow_strings=True)
    totalParkingCapacityShortTerm: int = IntegerValidator(allow_strings=True)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        static_parking_site = StaticParkingSiteInput(
            uid=self.id,
            purpose=PurposeType.CAR,
            name=self.parkingFacilityName,
            type=self.parkingFacilityLayout.to_parking_site_type(),
            static_data_updated_at=self.parkingFacilityRecordVersionTime,
            lat=self.facilityLocation.locationForDisplay.latitude,
            lon=self.facilityLocation.locationForDisplay.longitude,
            capacity=self.totalParkingCapacity,
            operator_name=self.owner.contactName,
        )
        for assigned_parking_space in self.assignedParkingSpaces:
            sub_capacity = assigned_parking_space.assignedParkingSpaces.get_sub_capacity()
            if sub_capacity is None:
                continue
            setattr(
                static_parking_site,
                sub_capacity,
                assigned_parking_space.assignedParkingSpaces.numberOfAssignedParkingSpaces,
            )

        return static_parking_site
