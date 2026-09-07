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
    RegexValidator,
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
    SAFE_WALL_LOOPS = 'Vorderradhalter mit Rahmen-Sicherung'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.STANDS: ParkingSiteType.STANDS,
            self.WALL_LOOPS: ParkingSiteType.WALL_LOOPS,
            self.SAFE_WALL_LOOPS: ParkingSiteType.SAFE_WALL_LOOPS,
        }.get(self)


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
    # A street name is required, and has to have at least one non-whitespace character to be a real value
    Strasse: str = RegexValidator(pattern=r'.*\S.*', max_length=256)
    Lagebeschreibung: str | None = EmptystringNoneable(StringValidator(max_length=4096)), Default(None)
    Stellplatzart: NagoldBikeStandType = EnumValidator(NagoldBikeStandType)
    Anzahl_Buegel_Stellplaetze: int = IntegerValidator(min_value=0, allow_strings=True)
    Anzahl_Schliessfaecher: int = IntegerValidator(min_value=0, allow_strings=True), Default(0)
    Anzahl_Lademoeglichkeiten: int = IntegerValidator(min_value=0, allow_strings=True), Default(0)
    Beleuchtung: bool | None = (
        EmptystringNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        Default(None),
    )
    Ueberdachung: bool | None = (
        EmptystringNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        Default(None),
    )
    Immer_geoeffnet_zugaenglich: bool | None = (
        EmptystringNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        Default(None),
    )
    Bike_and_Ride: NagoldBikeParkAndRideType | None = (
        EmptystringNoneable(EnumValidator(NagoldBikeParkAndRideType)),
        Default(None),
    )
    Ueberwachung: NagoldBikeSupervisionType | None = (
        EmptystringNoneable(EnumValidator(NagoldBikeSupervisionType)),
        Default(None),
    )
    Betreiber: str | None = EmptystringNoneable(StringValidator(max_length=256)), Default(None)
    Gebueren_pro_Tag_Cent: int | None = (
        EmptystringNoneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    Gebueren_pro_Monat_Cent: int | None = (
        EmptystringNoneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    Gebueren_pro_Jahr_Cent: int | None = (
        EmptystringNoneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    Beschreibung_Kostenkonditionen: str | None = EmptystringNoneable(StringValidator(max_length=2048)), Default(None)
    last_edited_date: datetime = TimestampDateTimeValidator(allow_strings=True, divisor=1000)

    @property
    def description(self) -> str | None:
        """
        The source has trailing whitespace in several location descriptions.
        """
        return self.Lagebeschreibung.strip() or None if self.Lagebeschreibung else None

    @property
    def fees_in_cent(self) -> list[tuple[int, str]]:
        return [
            (fee, interval)
            for fee, interval in [
                (self.Gebueren_pro_Tag_Cent, 'pro Tag'),
                (self.Gebueren_pro_Monat_Cent, 'pro Monat'),
                (self.Gebueren_pro_Jahr_Cent, 'pro Jahr'),
            ]
            if fee is not None
        ]

    @property
    def has_fee(self) -> bool | None:
        """
        Without any fee value the source does not tell if there is a fee, so the result stays unknown.
        """
        if not self.fees_in_cent:
            return None

        return any(fee > 0 for fee, _ in self.fees_in_cent)

    @property
    def fee_description(self) -> str | None:
        fee_descriptions = [
            f'{fee / 100:.2f} € {interval}'.replace('.', ',') for fee, interval in self.fees_in_cent if fee > 0
        ]

        if self.Beschreibung_Kostenkonditionen:
            fee_descriptions.append(self.Beschreibung_Kostenkonditionen)

        return ', '.join(fee_descriptions) or None


@validataclass
class NagoldBikeFeatureInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: NagoldBikePropertiesInput = DataclassValidator(NagoldBikePropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])

    def to_static_parking_sites(self) -> list[StaticParkingSiteInput]:
        """
        A feature can describe two installations at the same location: the bike stands themselves and, if
        Anzahl_Schliessfaecher is set, additional lockers. As both have their own type and capacity, they become two
        separate ParkingSites.
        """
        restrictions: list[ParkingSiteRestrictionInput] = []
        if self.properties.Anzahl_Lademoeglichkeiten > 0:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                    capacity=self.properties.Anzahl_Lademoeglichkeiten,
                ),
            )

        static_parking_sites = [
            self._to_static_parking_site(
                uid=str(self.properties.OBJECTID),
                name=self.properties.Strasse,
                parking_site_type=self.properties.Stellplatzart.to_parking_site_type(),
                capacity=self.properties.Anzahl_Buegel_Stellplaetze,
                restrictions=restrictions,
            ),
        ]

        if self.properties.Anzahl_Schliessfaecher > 0:
            static_parking_sites.append(
                self._to_static_parking_site(
                    uid=f'{self.properties.OBJECTID}-lockers',
                    name=f'{self.properties.Strasse} (Schließfächer)',
                    parking_site_type=ParkingSiteType.LOCKERS,
                    capacity=self.properties.Anzahl_Schliessfaecher,
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
            description=self.properties.description,
            operator_name=self.properties.Betreiber,
            purpose=PurposeType.BIKE,
            type=parking_site_type,
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            capacity=capacity,
            has_lighting=self.properties.Beleuchtung,
            is_covered=self.properties.Ueberdachung,
            has_fee=self.properties.has_fee,
            fee_description=self.properties.fee_description,
            opening_hours='24/7' if self.properties.Immer_geoeffnet_zugaenglich else None,
            park_and_ride_type=(
                [] if self.properties.Bike_and_Ride is None else self.properties.Bike_and_Ride.to_park_and_ride_types()
            ),
            supervision_type=(
                None if self.properties.Ueberwachung is None else self.properties.Ueberwachung.to_supervision_type()
            ),
            restrictions=restrictions,
            has_realtime_data=False,
            static_data_updated_at=self.properties.last_edited_date,
        )
