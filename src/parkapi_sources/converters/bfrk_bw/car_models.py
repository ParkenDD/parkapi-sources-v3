"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    BooleanValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import (
    ParkingSiteRestrictionInput,
    ParkingSpotRestrictionInput,
    StaticParkingSiteInput,
    StaticParkingSpotInput,
)
from parkapi_sources.models.enums import (
    ParkAndRideType,
    ParkingAudience,
    ParkingSiteOrientation,
    ParkingSiteType,
    ParkingSpotType,
)
from parkapi_sources.util import generate_point, round_7d
from parkapi_sources.validators import EmptystringNoneable, ReplacingStringValidator

from .base_models import BfrkBaseInput


class BfrkArt(Enum):
    PARK_AND_RIDE_PARKING_SITE = 'Park+Ride'
    SHORT_TERM_PARKING_SITE = 'Kurzzeit'
    DISABLED_PARKING_SPACE = 'Behindertenplätze'
    OFF_STREET_PARKING_GROUND = 'Parkplatz'
    OFF_STREET_PARKING_GROUND_2 = 'Parkplatz_ohne_Park+Ride'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.PARK_AND_RIDE_PARKING_SITE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.SHORT_TERM_PARKING_SITE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.DISABLED_PARKING_SPACE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND_2: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)


class BfrkBauart(Enum):
    CAR_PARK = 'parkhaus_hoch'
    UNDERGROUND = 'parkhaus_tief'
    OFF_STREET_PARKING_GROUND = 'parkplatz'
    OFF_STREET_PARKING_GROUND_2 = 'strasse_parkbucht'
    ON_STREET = 'auf_strasse'

    def to_parking_spot_type(self) -> ParkingSpotType:
        return {
            self.CAR_PARK: ParkingSpotType.CAR_PARK,
            self.UNDERGROUND: ParkingSpotType.UNDERGROUND,
            self.OFF_STREET_PARKING_GROUND: ParkingSpotType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND_2: ParkingSpotType.OFF_STREET_PARKING_GROUND,
            self.ON_STREET: ParkingSpotType.ON_STREET,
        }.get(self)


class Orientierung(Enum):
    PARALLEL = 'laengs'
    PERPENDICULAR = 'quer'
    DIAGONAL = 'diagonal'

    def to_parking_site_orientation_type(self) -> ParkingSiteOrientation:
        return {
            self.PARALLEL: ParkingSiteOrientation.PARALLEL,
            self.PERPENDICULAR: ParkingSiteOrientation.PERPENDICULAR,
            self.DIAGONAL: ParkingSiteOrientation.DIAGONAL,
        }.get(self)


@validataclass
class BfrkCarInput(BfrkBaseInput):
    art: BfrkArt | None = Noneable(EnumValidator(BfrkArt)), Default(BfrkArt.OFF_STREET_PARKING_GROUND)
    bauart: BfrkBauart | None = Noneable(EnumValidator(BfrkBauart)), Default(None)
    orientierung: Orientierung | None = Noneable(EnumValidator(Orientierung)), Default(None)
    stellplaetzegesamt: int = IntegerValidator()
    behindertenstellplaetze: int | None = Noneable(IntegerValidator()), Default(None)
    frauenstellplaetze: int | None = Noneable(IntegerValidator()), Default(None)
    familienstellplaetze: int | None = Noneable(IntegerValidator()), Default(None)
    bedingungen: str | None = EmptystringNoneable(ReplacingStringValidator(mapping={'\x80': '€'})), Default(None)
    eigentuemer: str | None = EmptystringNoneable(StringValidator()), Default(None)

    oeffnungszeiten: str | None = EmptystringNoneable(StringValidator()), Default(None)
    offen_24_7: bool | None = Noneable(BooleanValidator()), Default(None)

    behindertenplaetze_lat: Decimal | None = (
        NumericValidator(min_value=Decimal('47.5'), max_value=Decimal('49.8')),
        Default(None),
    )
    behindertenplaetze_lon: Decimal | None = (
        NumericValidator(min_value=Decimal('7.5'), max_value=Decimal('10.5')),
        Default(None),
    )
    behindertenplaetze_Foto: str | None = EmptystringNoneable(UrlValidator()), Default(None)

    maxparkdauer_min: int | None = Noneable(IntegerValidator()), Default(None)
    gebuehrenpflichtig: str | None = Noneable(StringValidator()), Default(None)
    gebuehrenbeispiele: str | None = Noneable(StringValidator()), Default(None)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            type=self.art.to_parking_site_type(),
            capacity=self.stellplaetzegesamt,
            description=self.bedingungen,
            operator_name=self.eigentuemer,
            **self.get_static_parking_site_input_kwargs(),
        )
        if self.behindertenstellplaetze is not None and self.behindertenstellplaetze > 0:
            static_parking_site_input.restrictions = [
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.DISABLED,
                    capacity=self.behindertenstellplaetze,
                ),
            ]

        if self.art == BfrkArt.PARK_AND_RIDE_PARKING_SITE:
            static_parking_site_input.park_and_ride_type = [ParkAndRideType.YES]

        return static_parking_site_input

    def to_static_parking_spot_inputs(self) -> list[StaticParkingSpotInput] | None:
        if (
            self.behindertenplaetze_lat is None
            or self.behindertenplaetze_lon is None
            or self.behindertenstellplaetze is None
        ):
            return None

        static_parking_spot_inputs: list[StaticParkingSpotInput] = []
        for i in range(self.behindertenstellplaetze):
            lat, lon = generate_point(
                lat=round_7d(self.behindertenplaetze_lat),
                lon=round_7d(self.behindertenplaetze_lon),
                number=i,
                max_number=self.behindertenstellplaetze,
            )
            static_parking_spot_inputs.append(
                StaticParkingSpotInput(
                    uid=f'{self.infraid}-{i}',
                    parking_site_uid=self.infraid,
                    static_data_updated_at=datetime.now(tz=timezone.utc),
                    has_realtime_data=False,
                    lat=lat,
                    lon=lon,
                    operator_name=self.eigentuemer,
                    photo_url=self.behindertenplaetze_Foto,
                    address=self._get_address(),
                    external_identifiers=self._get_external_identifiers(),
                    restrictions=[ParkingSpotRestrictionInput(type=ParkingAudience.DISABLED)],
                ),
            )

        return static_parking_spot_inputs
