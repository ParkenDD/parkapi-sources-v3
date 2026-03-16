"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from isodate import Duration
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
    ParkingType,
)
from parkapi_sources.util import generate_point, round_7d
from parkapi_sources.validators import EmptystringNoneable, ReplacingStringValidator

from .base_models import BfrkBaseInput

_KEINE_BEDINGUNGEN = {'keine', 'keine Angabe', 'keine Angaben'}


class BfrkArt(Enum):
    CAR_PARK = 'Parkhaus'
    OFF_STREET_PARKING_GROUND = 'Park+Ride'
    OFF_STREET_PARKING_GROUND_2 = 'Parkplatz_ohne_Park+Ride'
    OFF_STREET_PARKING_GROUND_3 = 'Kurzzeit'
    OFF_STREET_PARKING_GROUND_4 = 'Behindertenplätze'
    UNKNOWN = 'unbekannt'
    CUSTOMER = 'kundenparkplatz'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
            self.OFF_STREET_PARKING_GROUND: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND_2: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND_3: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND_4: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.UNKNOWN: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.CUSTOMER: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)

    def to_parking_spot_type(self) -> ParkingSpotType:
        return {
            self.CAR_PARK: ParkingSpotType.CAR_PARK,
            self.OFF_STREET_PARKING_GROUND: ParkingSpotType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND_2: ParkingSpotType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND_3: ParkingSpotType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND_4: ParkingSpotType.OFF_STREET_PARKING_GROUND,
        }.get(self)

    def to_name(self) -> str:
        return {self.CAR_PARK: 'Parkhaus'}.get(self, 'Parkplatz')


class BfrkBauart(Enum):
    CAR_PARK = 'parkhaus_hoch'
    UNDERGROUND = 'parkhaus_tief'
    OFF_STREET_PARKING_GROUND = 'parkplatz'
    ON_STREET = 'strasse_parkbucht'
    ON_STREET_2 = 'auf_strasse'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
            self.UNDERGROUND: ParkingSiteType.UNDERGROUND,
            self.OFF_STREET_PARKING_GROUND: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.ON_STREET: ParkingSiteType.ON_STREET,
            self.ON_STREET_2: ParkingSiteType.ON_STREET,
        }.get(self)

    def to_parking_spot_type(self) -> ParkingSpotType:
        return {
            self.CAR_PARK: ParkingSpotType.CAR_PARK,
            self.UNDERGROUND: ParkingSpotType.UNDERGROUND,
            self.OFF_STREET_PARKING_GROUND: ParkingSpotType.OFF_STREET_PARKING_GROUND,
            self.ON_STREET: ParkingSpotType.ON_STREET,
            self.ON_STREET_2: ParkingSpotType.ON_STREET,
        }.get(self)

    def to_name(self) -> str:
        return {
            self.CAR_PARK: 'Parkhaus',
            self.UNDERGROUND: 'Tiefgarage',
            self.OFF_STREET_PARKING_GROUND: 'Parkplatz',
            self.ON_STREET: 'Straßen-Parkplatz',
            self.ON_STREET_2: 'Straßen-Parkplatz',
        }.get(self)

    def to_parking_type(self) -> ParkingType | None:
        return {
            self.ON_STREET: ParkingType.ON_KERB,
            self.ON_STREET_2: ParkingType.LANE,
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
    art: BfrkArt = EnumValidator(BfrkArt), Default(BfrkArt.OFF_STREET_PARKING_GROUND)
    bauart: BfrkBauart | None = Noneable(EnumValidator(BfrkBauart)), Default(None)
    orientierung: Orientierung | None = Noneable(EnumValidator(Orientierung)), Default(None)
    stellplaetzegesamt: int = IntegerValidator(), Default(0)
    behindertenstellplaetze: int | None = Noneable(IntegerValidator()), Default(None)
    frauenstellplaetze: int | None = Noneable(IntegerValidator()), Default(None)
    familienstellplaetze: int | None = Noneable(IntegerValidator()), Default(None)
    bedingungen: str | None = EmptystringNoneable(ReplacingStringValidator(mapping={'\x80': '€'})), Default(None)
    eigentuemer: str | None = EmptystringNoneable(StringValidator()), Default(None)

    oeffnungszeiten: str | None = EmptystringNoneable(StringValidator()), Default(None)
    offen_24_7: bool | None = Noneable(BooleanValidator()), Default(None)

    oeffentlichvorhanden: bool | None = Noneable(BooleanValidator()), Default(None)

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
    gebuehrenbeispiele: str | None = Noneable(ReplacingStringValidator(mapping={'\x80': ''})), Default(None)

    def _get_description(self) -> str | None:
        if self.bedingungen is None or self.bedingungen in _KEINE_BEDINGUNGEN:
            return None
        return self.bedingungen

    def _get_opening_hours(self) -> str | None:
        if self.oeffnungszeiten:
            return self.oeffnungszeiten
        if self.offen_24_7:
            return '24/7'
        return None

    def _get_has_fee(self) -> bool | None:
        if self.gebuehrenpflichtig == 'ja':
            return True
        if self.gebuehrenpflichtig == 'nein':
            return False
        return None

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        if self.bauart is not None:
            parking_site_type = self.bauart.to_parking_site_type()
            name = self.bauart.to_name()
        else:
            parking_site_type = self.art.to_parking_site_type()
            name = self.art.to_name()

        static_parking_site_input = StaticParkingSiteInput(
            type=parking_site_type,
            capacity=self.stellplaetzegesamt,
            description=self._get_description(),
            operator_name=self.eigentuemer,
            orientation=self.orientierung.to_parking_site_orientation_type() if self.orientierung else None,
            parking_type=self.bauart.to_parking_type() if self.bauart else None,
            opening_hours=self._get_opening_hours(),
            has_fee=self._get_has_fee(),
            fee_description=self.gebuehrenbeispiele,
            **self.get_static_parking_site_input_kwargs(),
        )
        static_parking_site_input.name = name

        restrictions: list[ParkingSiteRestrictionInput] = []
        if self.behindertenstellplaetze is not None and self.behindertenstellplaetze > 0:
            restrictions.append(
                ParkingSiteRestrictionInput(type=ParkingAudience.DISABLED, capacity=self.behindertenstellplaetze),
            )
        if self.frauenstellplaetze is not None and self.frauenstellplaetze > 0:
            restrictions.append(
                ParkingSiteRestrictionInput(type=ParkingAudience.WOMEN, capacity=self.frauenstellplaetze),
            )
        if self.familienstellplaetze is not None and self.familienstellplaetze > 0:
            restrictions.append(
                ParkingSiteRestrictionInput(type=ParkingAudience.FAMILY, capacity=self.familienstellplaetze),
            )
        if self.maxparkdauer_min is not None and self.maxparkdauer_min != -1:
            restrictions.append(ParkingSiteRestrictionInput(max_stay=Duration(minutes=self.maxparkdauer_min)))
        if restrictions:
            static_parking_site_input.restrictions = restrictions

        if self.art == BfrkArt.OFF_STREET_PARKING_GROUND:
            static_parking_site_input.park_and_ride_type = [ParkAndRideType.YES]

        return static_parking_site_input

    def to_static_parking_spot_inputs(self) -> list[StaticParkingSpotInput] | None:
        if (
            self.behindertenplaetze_lat is None
            or self.behindertenplaetze_lon is None
            or self.behindertenstellplaetze is None
            or self.behindertenstellplaetze < 1
        ):
            return None

        if self.bauart is not None:
            spot_type = self.bauart.to_parking_spot_type()
            name = self.bauart.to_name()
        else:
            spot_type = self.art.to_parking_spot_type()
            name = self.art.to_name()

        description = self._get_description()

        restrictions: list[ParkingSpotRestrictionInput] = [ParkingSpotRestrictionInput(type=ParkingAudience.DISABLED)]
        if self.maxparkdauer_min is not None and self.maxparkdauer_min != -1:
            restrictions.append(ParkingSpotRestrictionInput(max_stay=Duration(minutes=self.maxparkdauer_min)))

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
                    name=name,
                    type=spot_type,
                    description=description,
                    static_data_updated_at=datetime.now(tz=timezone.utc),
                    has_realtime_data=False,
                    lat=lat,
                    lon=lon,
                    operator_name=self.eigentuemer,
                    photo_url=self.behindertenplaetze_Foto,
                    address=self._get_address(),
                    external_identifiers=self._get_external_identifiers(),
                    restrictions=restrictions,
                ),
            )

        return static_parking_spot_inputs
