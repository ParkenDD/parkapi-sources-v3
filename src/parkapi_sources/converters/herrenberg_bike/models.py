"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime, time, timezone
from enum import Enum
from typing import Optional

from validataclass.dataclasses import DefaultUnset, ValidataclassMixin, validataclass
from validataclass.helpers import OptionalUnset, UnsetValue
from validataclass.validators import (
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    NoneToUnsetValue,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.converters.base_converter.pull import GeojsonFeatureGeometryInput
from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType, SupervisionType
from parkapi_sources.validators import MappedBooleanValidator, ParsedDateValidator


class HerrenbergBikeType(Enum):
    STANDS = 'stands'
    WALL_LOOPS = 'wall_loops'
    RACK = 'rack'
    SHED = 'shed'
    BOLLARD = 'bollard'
    WIDE_STANDS = 'wide_stands'
    BUILDING = 'building'
    LOCKERS = 'lockers'
    WAVE = 'wave'
    ANCHORS = 'anchors'
    FLOOR = 'floor'
    SAFE_LOOPS = 'safe_loops'
    GROUND_SLOTS = 'ground_slots'
    LEAN_AND_STICK = 'lean_and_stick'
    CROSSBAR = 'crossbar'
    OTHER = 'other'

    def to_parking_site_type(self) -> ParkingSiteType:
        if self in [
            self.OTHER,
            self.BOLLARD,
            self.LEAN_AND_STICK,
            self.WAVE,
            self.ANCHORS,
            self.CROSSBAR,
            self.RACK,
            self.GROUND_SLOTS,
        ]:
            return ParkingSiteType.OTHER
        return {
            self.SAFE_LOOPS: ParkingSiteType.SAFE_WALL_LOOPS,
            self.WIDE_STANDS: ParkingSiteType.STANDS,
            self.STANDS: ParkingSiteType.STANDS,
            self.SHED: ParkingSiteType.SHED,
            self.BUILDING: ParkingSiteType.BUILDING,
            self.LOCKERS: ParkingSiteType.LOCKERS,
            self.FLOOR: ParkingSiteType.FLOOR,
            self.WALL_LOOPS: ParkingSiteType.WALL_LOOPS,
        }.get(self)


class HerrenbergBikeAccessType(Enum):
    YES = 'yes'
    PRIVATE = 'private'
    CUSTOMERS = 'customers'
    MEMBERS = 'members'


class HerrenbergBikeSupervisionType(Enum):
    YES = 'ja'
    NO = 'nein'
    VIDEO = 'video'
    BEWACHT = 'bewacht'
    UNKNOWN = 'unbekannt'

    def to_supervision_type(self) -> SupervisionType:
        return {
            self.YES: SupervisionType.YES,
            self.NO: SupervisionType.NO,
            self.VIDEO: SupervisionType.VIDEO,
            self.BEWACHT: SupervisionType.ATTENDED,
        }.get(self)


@validataclass
class HerrenbergBikeAddressInput:
    street: Optional[str] = Noneable(StringValidator(max_length=512))
    houseNo: Optional[str] = Noneable(StringValidator(max_length=512))
    zipCode: Optional[str] = Noneable(StringValidator(max_length=512))
    location: Optional[str] = Noneable(StringValidator(max_length=512))


@validataclass
class HerrenbergBikePropertiesInput(ValidataclassMixin):
    original_uid: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(min_length=0, max_length=256)
    type: OptionalUnset[HerrenbergBikeType] = NoneToUnsetValue(EnumValidator(HerrenbergBikeType)), DefaultUnset
    public_url: OptionalUnset[str] = NoneToUnsetValue(UrlValidator(max_length=4096)), DefaultUnset
    address: OptionalUnset[HerrenbergBikeAddressInput] = (
        NoneToUnsetValue(DataclassValidator(HerrenbergBikeAddressInput)),
        DefaultUnset,
    )
    description: OptionalUnset[str] = NoneToUnsetValue(StringValidator(max_length=512)), DefaultUnset
    operator_name: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    capacity: int = IntegerValidator(min_value=0)
    capacity_charging: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    capacity_cargobike: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    max_height: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    max_width: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    supervision_type: OptionalUnset[HerrenbergBikeSupervisionType] = (
        NoneToUnsetValue(EnumValidator(HerrenbergBikeSupervisionType)),
        DefaultUnset,
    )
    has_realtime_data: OptionalUnset[bool] = (
        NoneToUnsetValue(MappedBooleanValidator(mapping={'true': True, 'false': False})),
        DefaultUnset,
    )
    access: OptionalUnset[HerrenbergBikeAccessType] = (
        NoneToUnsetValue(EnumValidator(HerrenbergBikeAccessType)),
        DefaultUnset,
    )
    date_surveyed: OptionalUnset[date] = NoneToUnsetValue(ParsedDateValidator(date_format='%Y-%m-%d')), DefaultUnset
    has_lighting: OptionalUnset[bool] = (
        NoneToUnsetValue(MappedBooleanValidator(mapping={'true': True, 'false': False})),
        DefaultUnset,
    )
    has_fee: OptionalUnset[bool] = (
        NoneToUnsetValue(MappedBooleanValidator(mapping={'true': True, 'false': False})),
        DefaultUnset,
    )
    is_covered: OptionalUnset[bool] = (
        NoneToUnsetValue(MappedBooleanValidator(mapping={'true': True, 'false': False})),
        DefaultUnset,
    )
    related_location: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    opening_hours: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    max_stay: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    fee_description: OptionalUnset[str] = NoneToUnsetValue(StringValidator(max_length=512)), DefaultUnset


@validataclass
class HerrenbergBikeFeatureInput:
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)
    properties: HerrenbergBikePropertiesInput = DataclassValidator(HerrenbergBikePropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.properties.original_uid),
            name=self.properties.name if self.properties.name != '' else 'Fahrrad-Abstellanlagen',
            type=self.properties.type.to_parking_site_type(),
            description=self.properties.description,
            capacity=self.properties.capacity,
            has_realtime_data=self.properties.has_realtime_data,
            has_lighting=self.properties.has_lighting,
            is_covered=self.properties.is_covered,
            related_location=self.properties.related_location,
            operator_name=self.properties.operator_name,
            max_height=self.properties.max_height,
            max_width=self.properties.max_width,
            has_fee=self.properties.has_fee,
            supervision_type=self.properties.supervision_type.to_supervision_type()
            if self.properties.supervision_type is not UnsetValue
            else UnsetValue,
            fee_description=self.properties.fee_description,
            capacity_charging=self.properties.capacity_charging,
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            static_data_updated_at=datetime.now(timezone.utc)
            if self.properties.date_surveyed is UnsetValue
            else datetime.combine(self.properties.date_surveyed, time(), tzinfo=timezone.utc),
            purpose=PurposeType.BIKE,
        )
