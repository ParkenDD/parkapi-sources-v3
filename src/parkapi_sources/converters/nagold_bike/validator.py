"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from enum import Enum

from shapely import GeometryType, Point
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnyOfValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    StringValidator,
)

from parkapi_sources.models import ParkingSiteRestrictionInput, StaticParkingSiteInput
from parkapi_sources.models.enums import (
    ParkAndRideType,
    ParkingAudience,
    ParkingSiteType,
    PurposeType,
    SupervisionType,
)
from parkapi_sources.util import round_7d
from parkapi_sources.validators import (
    EmptystringNoneable,
    GeoJSONGeometryValidator,
    MappedBooleanValidator,
    TimestampDateTimeValidator,
)


class NagoldBikeStandType(Enum):
    STANDS = 'Anlehnbügel'
    WALL_LOOPS = 'Vorderradanschluss'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.STANDS: ParkingSiteType.STANDS,
            self.WALL_LOOPS: ParkingSiteType.WALL_LOOPS,
        }.get(self, ParkingSiteType.OTHER)


class NagoldBikeParkAndRideType(Enum):
    YES = 'ja'
    NO = 'nein'

    def to_park_and_ride_types(self) -> list[ParkAndRideType]:
        return {
            self.YES: [ParkAndRideType.YES],
            self.NO: [ParkAndRideType.NO],
        }.get(self, [])


class NagoldBikeSupervisionType(Enum):
    YES = 'ja'
    NO = 'nein'

    def to_supervision_type(self) -> SupervisionType | None:
        return {
            self.YES: SupervisionType.YES,
            self.NO: SupervisionType.NO,
        }.get(self)


@validataclass
class NagoldBikePropertiesInput:
    OBJECTID: int = IntegerValidator(allow_strings=True)
    Strasse: str = StringValidator(min_length=1, max_length=256)
    Lagebeschr: str | None = EmptystringNoneable(StringValidator(max_length=4096)), Default(None)
    Stellplatz: NagoldBikeStandType = EnumValidator(NagoldBikeStandType)
    Anzahl_Bue: int = IntegerValidator(min_value=0, allow_strings=True)
    Anzahl_Sch: int = IntegerValidator(min_value=0, allow_strings=True), Default(0)
    Anzahl_Lad: int = IntegerValidator(min_value=0, allow_strings=True), Default(0)
    Beleuchtun: bool | None = (
        EmptystringNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        Default(None),
    )
    Ueberdachu: bool | None = (
        EmptystringNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        Default(None),
    )
    Immer_geoe: bool | None = (
        EmptystringNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        Default(None),
    )
    Bike_and_R: NagoldBikeParkAndRideType | None = (
        EmptystringNoneable(EnumValidator(NagoldBikeParkAndRideType)),
        Default(None),
    )
    Ueberwachu: NagoldBikeSupervisionType | None = (
        EmptystringNoneable(EnumValidator(NagoldBikeSupervisionType)),
        Default(None),
    )
    Betreiber: str | None = EmptystringNoneable(StringValidator(max_length=256)), Default(None)
    Gebueren_p: bool | None = (
        EmptystringNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        Default(None),
    )
    Gebueren_1: str | None = EmptystringNoneable(StringValidator(max_length=2048)), Default(None)
    Gebueren_2: str | None = EmptystringNoneable(StringValidator(max_length=2048)), Default(None)
    last_edi_1: datetime = TimestampDateTimeValidator(allow_strings=True, divisor=1000)

    @property
    def fee_description(self) -> str | None:
        return ', '.join(value for value in [self.Gebueren_1, self.Gebueren_2] if value) or None


@validataclass
class NagoldBikeFeatureInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: NagoldBikePropertiesInput = DataclassValidator(NagoldBikePropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])

    def to_static_parking_sites(self) -> list[StaticParkingSiteInput]:
        """
        A feature can describe two installations at the same location: the bike stands themselves and, if Anzahl_Sch
        is set, additional lockers. As both have their own type and capacity, they become two separate ParkingSites.
        """
        restrictions: list[ParkingSiteRestrictionInput] = []
        if self.properties.Anzahl_Lad > 0:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                    capacity=self.properties.Anzahl_Lad,
                ),
            )

        static_parking_sites = [
            self._to_static_parking_site(
                uid=str(self.properties.OBJECTID),
                name=self.properties.Strasse,
                parking_site_type=self.properties.Stellplatz.to_parking_site_type(),
                capacity=self.properties.Anzahl_Bue,
                restrictions=restrictions,
            ),
        ]

        if self.properties.Anzahl_Sch > 0:
            static_parking_sites.append(
                self._to_static_parking_site(
                    uid=f'{self.properties.OBJECTID}-lockers',
                    name=f'{self.properties.Strasse} (Schließfächer)',
                    parking_site_type=ParkingSiteType.LOCKERS,
                    capacity=self.properties.Anzahl_Sch,
                    restrictions=[],
                ),
            )

        return static_parking_sites

    def _to_static_parking_site(
        self,
        uid: str,
        name: str,
        parking_site_type: ParkingSiteType,
        capacity: int,
        restrictions: list[ParkingSiteRestrictionInput],
    ) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=uid,
            name=name,
            # The source has no house numbers, so the address is limited to the street
            address=f'{self.properties.Strasse}, 72202 Nagold',
            description=self.properties.Lagebeschr,
            operator_name=self.properties.Betreiber,
            purpose=PurposeType.BIKE,
            type=parking_site_type,
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            capacity=capacity,
            has_lighting=self.properties.Beleuchtun,
            is_covered=self.properties.Ueberdachu,
            has_fee=self.properties.Gebueren_p,
            fee_description=self.properties.fee_description,
            opening_hours='24/7' if self.properties.Immer_geoe else None,
            park_and_ride_type=(
                [] if self.properties.Bike_and_R is None else self.properties.Bike_and_R.to_park_and_ride_types()
            ),
            supervision_type=(
                None if self.properties.Ueberwachu is None else self.properties.Ueberwachu.to_supervision_type()
            ),
            restrictions=restrictions,
            has_realtime_data=False,
            static_data_updated_at=self.properties.last_edi_1,
        )
