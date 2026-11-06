"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any
from zoneinfo import ZoneInfo

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnythingValidator,
    DataclassValidator,
    DateTimeValidator,
    DecimalValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    StringValidator,
)

from parkapi_sources.converters.base_converter.datex2.multilingual_string import get_localised_text
from parkapi_sources.models import ParkingSiteRestrictionInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkAndRideType, ParkingAudience, ParkingSiteType, PurposeType
from parkapi_sources.validators import MappedBooleanValidator


class ParkingLayout(Enum):
    MULTI_STOREY = 'multiStorey'
    SINGLE_LEVEL = 'singleLevel'
    UNDERGROUND = 'underground'
    UNDERGROUND_AND_MULTI_STOREY = 'undergroundAndMultistorey'
    AUTOMATED_PARKING_GARAGE = 'automatedParkingGarage'
    OPEN_SPACE = 'openSpace'
    COVERED = 'covered'
    NESTED = 'nested'
    FIELD = 'field'
    UNKNOWN = 'unknown'
    OTHER = 'other'

    def to_parking_site_type(self) -> ParkingSiteType | None:
        return {
            self.MULTI_STOREY: ParkingSiteType.CAR_PARK,
            self.UNDERGROUND: ParkingSiteType.UNDERGROUND,
            self.UNDERGROUND_AND_MULTI_STOREY: ParkingSiteType.CAR_PARK,
            self.AUTOMATED_PARKING_GARAGE: ParkingSiteType.CAR_PARK,
            self.SINGLE_LEVEL: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OPEN_SPACE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.COVERED: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.FIELD: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)


class UrbanParkingSiteType(Enum):
    ON_STREET_PARKING = 'onStreetParking'
    OFF_STREET_PARKING = 'offStreetParking'
    OTHER = 'other'

    def to_parking_site_type(self) -> ParkingSiteType | None:
        return {
            self.ON_STREET_PARKING: ParkingSiteType.ON_STREET,
            self.OFF_STREET_PARKING: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)


class UserType(Enum):
    HANDICAPPED = 'handicapped'
    DISABLED = 'disabled'
    FAMILIES = 'families'
    WOMEN = 'women'

    def to_parking_audience(self) -> ParkingAudience:
        return {
            self.HANDICAPPED: ParkingAudience.DISABLED,
            self.DISABLED: ParkingAudience.DISABLED,
            self.FAMILIES: ParkingAudience.FAMILY,
            self.WOMEN: ParkingAudience.WOMEN,
        }[self]


class ComparisonOperator(Enum):
    EQUAL_TO = 'equalTo'
    GREATER_THAN = 'greaterThan'
    GREATER_THAN_OR_EQUAL_TO = 'greaterThanOrEqualTo'
    LESS_THAN = 'lessThan'
    LESS_THAN_OR_EQUAL_TO = 'lessThanOrEqualTo'


class ParkingUsageScenarioType(Enum):
    PARK_AND_RIDE = 'parkAndRide'
    CAR_SHARING = 'carSharing'
    OTHER = 'other'


@validataclass
class PointCoordinates:
    latitude: Decimal = DecimalValidator()
    longitude: Decimal = DecimalValidator()


@validataclass
class PointByCoordinates:
    pointCoordinates: PointCoordinates = DataclassValidator(PointCoordinates)


@validataclass
class ParkingLocation:
    pointByCoordinates: PointByCoordinates = DataclassValidator(PointByCoordinates)


@validataclass
class Operator:
    contactOrganisationName: Any = AnythingValidator(allowed_types=[str, dict, list]), Default(None)


@validataclass
class TariffsAndPayment:
    freeOfCharge: bool | None = MappedBooleanValidator(mapping={'true': True, 'false': False}), Default(None)


@validataclass
class OpeningTimes:
    available24hours: bool | None = MappedBooleanValidator(mapping={'true': True, 'false': False}), Default(None)


@validataclass
class HeightCharacteristic:
    comparisonOperator: ComparisonOperator = EnumValidator(ComparisonOperator)
    # DATEX II uses meters
    vehicleHeight: Decimal = DecimalValidator()


@validataclass
class VehicleCharacteristics:
    fuelType: str | None = StringValidator(), Default(None)
    heightCharacteristic: HeightCharacteristic | None = DataclassValidator(HeightCharacteristic), Default(None)


@validataclass
class AccessOnlyAssignedFor:
    vehicleCharacteristics: VehicleCharacteristics | None = DataclassValidator(VehicleCharacteristics), Default(None)


@validataclass
class ParkingAccess:
    accessOnlyAssignedFor: AccessOnlyAssignedFor | None = DataclassValidator(AccessOnlyAssignedFor), Default(None)

    def get_max_height(self) -> int | None:
        if self.accessOnlyAssignedFor is None or self.accessOnlyAssignedFor.vehicleCharacteristics is None:
            return None
        height_characteristic = self.accessOnlyAssignedFor.vehicleCharacteristics.heightCharacteristic
        if height_characteristic is None or height_characteristic.comparisonOperator not in (
            ComparisonOperator.LESS_THAN,
            ComparisonOperator.LESS_THAN_OR_EQUAL_TO,
        ):
            return None
        # ParkAPI uses centimeters
        return int(height_characteristic.vehicleHeight * 100)


@validataclass
class OnlyAssignedParking:
    applicableForUser: list[str] = ListValidator(StringValidator()), Default([])
    vehicleCharacteristics: VehicleCharacteristics | None = DataclassValidator(VehicleCharacteristics), Default(None)

    def get_parking_audience(self) -> ParkingAudience | None:
        for applicable_for_user in self.applicableForUser:
            if applicable_for_user in UserType:
                return UserType(applicable_for_user).to_parking_audience()
        if self.vehicleCharacteristics is not None and self.vehicleCharacteristics.fuelType == 'battery':
            return ParkingAudience.CHARGING
        return None


@validataclass
class ParkingSpaceBasics:
    parkingNumberOfSpaces: int | None = IntegerValidator(allow_strings=True), Default(None)
    onlyAssignedParking: OnlyAssignedParking | None = DataclassValidator(OnlyAssignedParking), Default(None)


@validataclass
class GroupOfParkingSpaces:
    parkingSpaceBasics: ParkingSpaceBasics = DataclassValidator(ParkingSpaceBasics)


@validataclass
class InnerParkingUsageScenario:
    parkingUsageScenario: ParkingUsageScenarioType = EnumValidator(ParkingUsageScenarioType)


@validataclass
class ParkingUsageScenario:
    parkingUsageScenario: InnerParkingUsageScenario = DataclassValidator(InnerParkingUsageScenario)


@validataclass
class UrbanParkingSite:
    id: str = StringValidator()
    parkingName: Any = AnythingValidator(allowed_types=[str, dict, list])
    parkingDescription: Any = AnythingValidator(allowed_types=[str, dict, list]), Default(None)
    parkingRecordVersionTime: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )
    parkingNumberOfSpaces: int = IntegerValidator(allow_strings=True)
    parkingLocation: ParkingLocation = DataclassValidator(ParkingLocation)
    urbanParkingSiteType: UrbanParkingSiteType = EnumValidator(UrbanParkingSiteType)
    parkingLayout: ParkingLayout | None = EnumValidator(ParkingLayout), Default(None)
    operator: Operator | None = DataclassValidator(Operator), Default(None)
    tariffsAndPayment: TariffsAndPayment | None = DataclassValidator(TariffsAndPayment), Default(None)
    openingTimes: OpeningTimes | None = DataclassValidator(OpeningTimes), Default(None)
    parkingAccess: list[ParkingAccess] = ListValidator(DataclassValidator(ParkingAccess)), Default([])
    groupOfParkingSpaces: list[GroupOfParkingSpaces] = (
        ListValidator(DataclassValidator(GroupOfParkingSpaces)),
        Default([]),
    )
    parkingUsageScenario: list[ParkingUsageScenario] = (
        ListValidator(DataclassValidator(ParkingUsageScenario)),
        Default([]),
    )

    def _get_parking_site_type(self) -> ParkingSiteType:
        if self.urbanParkingSiteType == UrbanParkingSiteType.ON_STREET_PARKING:
            return ParkingSiteType.ON_STREET
        if self.parkingLayout is not None and self.parkingLayout.to_parking_site_type() is not None:
            return self.parkingLayout.to_parking_site_type()
        return self.urbanParkingSiteType.to_parking_site_type() or ParkingSiteType.OTHER

    def _get_max_height(self) -> int | None:
        max_heights = [
            parking_access.get_max_height()
            for parking_access in self.parkingAccess
            if parking_access.get_max_height() is not None
        ]
        # The lowest access limits the vehicle height
        return min(max_heights) if max_heights else None

    def _get_restrictions(self) -> list[ParkingSiteRestrictionInput]:
        restrictions: list[ParkingSiteRestrictionInput] = []
        for group_of_parking_spaces in self.groupOfParkingSpaces:
            parking_space_basics = group_of_parking_spaces.parkingSpaceBasics
            if parking_space_basics.onlyAssignedParking is None or not parking_space_basics.parkingNumberOfSpaces:
                continue
            parking_audience = parking_space_basics.onlyAssignedParking.get_parking_audience()
            if parking_audience is None:
                continue
            restrictions.append(
                ParkingSiteRestrictionInput(type=parking_audience, capacity=parking_space_basics.parkingNumberOfSpaces),
            )
        return restrictions

    def to_static_parking_site_input(self, has_realtime_data: bool) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            uid=self.id,
            name=get_localised_text(self.parkingName),
            description=get_localised_text(self.parkingDescription),
            purpose=PurposeType.CAR,
            type=self._get_parking_site_type(),
            lat=self.parkingLocation.pointByCoordinates.pointCoordinates.latitude,
            lon=self.parkingLocation.pointByCoordinates.pointCoordinates.longitude,
            capacity=self.parkingNumberOfSpaces,
            static_data_updated_at=self.parkingRecordVersionTime,
            has_realtime_data=has_realtime_data,
            max_height=self._get_max_height(),
        )

        if self.operator is not None:
            static_parking_site_input.operator_name = get_localised_text(self.operator.contactOrganisationName)

        if self.tariffsAndPayment is not None and self.tariffsAndPayment.freeOfCharge is not None:
            static_parking_site_input.has_fee = not self.tariffsAndPayment.freeOfCharge

        if self.openingTimes is not None and self.openingTimes.available24hours is True:
            static_parking_site_input.opening_hours = '24/7'

        if self.parkingLayout == ParkingLayout.COVERED:
            static_parking_site_input.is_covered = True

        if any(
            parking_usage_scenario.parkingUsageScenario.parkingUsageScenario == ParkingUsageScenarioType.PARK_AND_RIDE
            for parking_usage_scenario in self.parkingUsageScenario
        ):
            static_parking_site_input.park_and_ride_type = [ParkAndRideType.YES]

        restrictions = self._get_restrictions()
        if restrictions:
            static_parking_site_input.restrictions = restrictions

        return static_parking_site_input
