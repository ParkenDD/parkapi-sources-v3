"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any
from zoneinfo import ZoneInfo

from validataclass.dataclasses import Default, validataclass
from validataclass.exceptions import DataclassPostValidationError, RequiredValueError
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

from parkapi_sources.models import ParkingSiteRestrictionInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingAudience, ParkingSiteType, PurposeType

from .multilingual_string import get_localised_text


class FacilityLayout(Enum):
    MULTI_STOREY = 'multiStorey'
    SINGLE_LEVEL = 'singleLevel'
    UNDERGROUND = 'underground'
    UNDERGROUND_AND_MULTI_STOREY = 'undergroundAndMultistorey'
    AUTOMATED_PARKING_GARAGE = 'automatedParkingGarage'

    def to_parking_site_type(self) -> ParkingSiteType | None:
        return {
            self.MULTI_STOREY: ParkingSiteType.CAR_PARK,
            self.SINGLE_LEVEL: ParkingSiteType.CAR_PARK,
            self.UNDERGROUND: ParkingSiteType.UNDERGROUND,
            self.UNDERGROUND_AND_MULTI_STOREY: ParkingSiteType.CAR_PARK,
            self.AUTOMATED_PARKING_GARAGE: ParkingSiteType.CAR_PARK,
        }.get(self)


class ComparisonOperator(Enum):
    EQUAL_TO = 'equalTo'
    GREATER_THAN = 'greaterThan'
    GREATER_THAN_OR_EQUAL_TO = 'greaterThanOrEqualTo'
    LESS_THAN = 'lessThan'
    LESS_THAN_OR_EQUAL_TO = 'lessThanOrEqualTo'


@validataclass
class InnerAssignedParkingSpace:
    descriptionOfAssignedParkingSpaces: dict = AnythingValidator(allowed_types=dict)
    numberOfAssignedParkingSpaces: int = IntegerValidator(allow_strings=True)

    def get_audience(self) -> ParkingAudience | None:
        if self.descriptionOfAssignedParkingSpaces == {'personTypeForWhichSpacesAssigned': 'women'}:
            return ParkingAudience.WOMEN
        if self.descriptionOfAssignedParkingSpaces == {'personTypeForWhichSpacesAssigned': 'families'}:
            return ParkingAudience.FAMILY
        if self.descriptionOfAssignedParkingSpaces == {'personTypeForWhichSpacesAssigned': 'disabled'}:
            return ParkingAudience.DISABLED
        if self.descriptionOfAssignedParkingSpaces == {
            'characteristicsOfVehiclesForWhichSpacesAssigned': {'fuelType': 'battery'}
        }:
            return ParkingAudience.CHARGING
        return None


@validataclass
class OuterAssignedParkingSpace:
    assignedParkingSpaces: InnerAssignedParkingSpace = DataclassValidator(InnerAssignedParkingSpace)


@validataclass
class Coordinates:
    latitude: Decimal = DecimalValidator()
    longitude: Decimal = DecimalValidator()


@validataclass
class PointByCoordinates:
    pointCoordinates: Coordinates = DataclassValidator(Coordinates)


@validataclass
class FacilityLocation:
    # Depending on the location type (Area or Point), the coordinates are given in one of these fields
    locationForDisplay: Coordinates | None = DataclassValidator(Coordinates), Default(None)
    pointByCoordinates: PointByCoordinates | None = DataclassValidator(PointByCoordinates), Default(None)

    def __post_init__(self):
        if self.locationForDisplay is None and self.pointByCoordinates is None:
            raise DataclassPostValidationError(
                field_errors={
                    'locationForDisplay': RequiredValueError(
                        reason='Either locationForDisplay or pointByCoordinates is required.',
                    ),
                },
            )

    @property
    def coordinates(self) -> Coordinates:
        if self.locationForDisplay is not None:
            return self.locationForDisplay
        return self.pointByCoordinates.pointCoordinates


@validataclass
class Owner:
    contactName: str | None = Noneable(StringValidator()), Default(None)


@validataclass
class HeightCharacteristic:
    comparisonOperator: ComparisonOperator = EnumValidator(ComparisonOperator)
    # DATEX II uses meters
    vehicleHeight: Decimal = DecimalValidator()


@validataclass
class CharacteristicsOfPermittedVehicles:
    heightCharacteristic: HeightCharacteristic | None = DataclassValidator(HeightCharacteristic), Default(None)


@validataclass
class ParkingFacility:
    id: str = StringValidator()
    # A multilingual string, which can be a plain string, a dict with lang and text or a list of both
    parkingFacilityName: Any = AnythingValidator(allowed_types=[str, dict, list])
    parkingFacilityRecordVersionTime: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    facilityLocation: FacilityLocation = DataclassValidator(FacilityLocation)
    parkingFacilityLayout: FacilityLayout | None = EnumValidator(FacilityLayout), Default(None)
    totalParkingCapacity: int | None = IntegerValidator(allow_strings=True), Default(None)
    totalParkingCapacityLongTerm: int | None = IntegerValidator(allow_strings=True), Default(None)
    totalParkingCapacityShortTerm: int | None = IntegerValidator(allow_strings=True), Default(None)
    owner: Owner | None = DataclassValidator(Owner), Default(None)
    characteristicsOfPermittedVehicles: CharacteristicsOfPermittedVehicles | None = (
        DataclassValidator(CharacteristicsOfPermittedVehicles),
        Default(None),
    )
    assignedParkingSpaces: list[OuterAssignedParkingSpace] = (
        ListValidator(DataclassValidator(OuterAssignedParkingSpace)),
        Default([]),
    )

    def __post_init__(self):
        if self.capacity is None:
            raise DataclassPostValidationError(
                field_errors={
                    'totalParkingCapacity': RequiredValueError(
                        reason='Either totalParkingCapacity or short and long term capacities are required.',
                    ),
                },
            )

    @property
    def capacity(self) -> int | None:
        if self.totalParkingCapacity is not None:
            return self.totalParkingCapacity
        # Without a total capacity, the short term and long term capacities add up to the total capacity
        if self.totalParkingCapacityShortTerm is None and self.totalParkingCapacityLongTerm is None:
            return None
        return (self.totalParkingCapacityShortTerm or 0) + (self.totalParkingCapacityLongTerm or 0)

    def _get_parking_site_type(self) -> ParkingSiteType:
        if self.parkingFacilityLayout is None:
            return ParkingSiteType.OTHER
        return self.parkingFacilityLayout.to_parking_site_type() or ParkingSiteType.OTHER

    def _get_max_height(self) -> int | None:
        if self.characteristicsOfPermittedVehicles is None:
            return None
        height_characteristic = self.characteristicsOfPermittedVehicles.heightCharacteristic
        if height_characteristic is None or height_characteristic.comparisonOperator not in (
            ComparisonOperator.LESS_THAN,
            ComparisonOperator.LESS_THAN_OR_EQUAL_TO,
        ):
            return None
        # ParkAPI uses centimeters
        return int(height_characteristic.vehicleHeight * 100)

    def to_static_parking_site_input(self, has_realtime_data: bool) -> StaticParkingSiteInput:
        static_parking_site = StaticParkingSiteInput(
            uid=self.id,
            purpose=PurposeType.CAR,
            name=get_localised_text(self.parkingFacilityName),
            type=self._get_parking_site_type(),
            static_data_updated_at=self.parkingFacilityRecordVersionTime,
            has_realtime_data=has_realtime_data,
            lat=self.facilityLocation.coordinates.latitude,
            lon=self.facilityLocation.coordinates.longitude,
            capacity=self.capacity,
            operator_name=self.owner.contactName if self.owner is not None else None,
            max_height=self._get_max_height(),
        )
        restrictions: list[ParkingSiteRestrictionInput] = []
        for assigned_parking_space in self.assignedParkingSpaces:
            audience = assigned_parking_space.assignedParkingSpaces.get_audience()
            if audience is None or assigned_parking_space.assignedParkingSpaces.numberOfAssignedParkingSpaces == 0:
                continue
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=audience,
                    capacity=assigned_parking_space.assignedParkingSpaces.numberOfAssignedParkingSpaces,
                )
            )
        if restrictions:
            static_parking_site.restrictions = restrictions

        return static_parking_site
