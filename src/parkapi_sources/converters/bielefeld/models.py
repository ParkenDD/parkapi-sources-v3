"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import EnumValidator, IntegerValidator, NumericValidator, StringValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkAndRideType, ParkingSiteType, PurposeType
from parkapi_sources.validators import ExcelNoneable, MappedBooleanValidator


class BielefeldType(Enum):
    P = 'P'
    PZ = 'PZ'
    H = 'H'
    HZ = 'HZ'
    T = 'T'
    TZ = 'TZ'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.P: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.PZ: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.H: ParkingSiteType.CAR_PARK,
            self.HZ: ParkingSiteType.CAR_PARK,
            self.T: ParkingSiteType.UNDERGROUND,
            self.TZ: ParkingSiteType.UNDERGROUND,
        }[self]


@validataclass
class BielefeldParkingSiteInput:
    gid: str = StringValidator()
    bez: str = StringValidator()
    wkt: str = StringValidator()
    typ: BielefeldType = EnumValidator(BielefeldType)
    kapazitaet: int | None = ExcelNoneable(IntegerValidator(min_value=0)), Default(None)
    hoehe: str | None = ExcelNoneable(StringValidator()), Default(None)
    einfahrtshoehe: Decimal | None = ExcelNoneable(NumericValidator()), Default(None)
    zufahrt: str | None = ExcelNoneable(StringValidator()), Default(None)
    gebuehren: bool | None = (
        ExcelNoneable(
            MappedBooleanValidator(
                mapping={
                    'ja': True,
                    'j': True,
                    'parkscheinautomat, handyparken': True,
                    '3 stunden frei': True,
                    '4 stunden frei': True,
                    'eine stunde kostenfrei': True,
                    'nein': False,
                    'ausweis': False,
                }
            )
        ),
        Default(None),
    )
    gebuehren_internet: str | None = ExcelNoneable(StringValidator()), Default(None)
    oeffi: str | None = ExcelNoneable(StringValidator()), Default(None)
    kategorie: str | None = ExcelNoneable(StringValidator()), Default(None)
    oeff_mo_fr: str | None = ExcelNoneable(StringValidator()), Default(None)
    oeff_sa: str | None = ExcelNoneable(StringValidator()), Default(None)
    oeff_so: str | None = ExcelNoneable(StringValidator()), Default(None)

    def _parse_wkt_coordinates(self) -> tuple[Decimal, Decimal]:
        match = re.match(r'POINT\s*\(\s*(\S+)\s+(\S+)\s*\)', self.wkt)
        lon = Decimal(match.group(1))
        lat = Decimal(match.group(2))
        return lat, lon

    def _get_max_height(self) -> int | None:
        if self.einfahrtshoehe is not None:
            height_cm = int(self.einfahrtshoehe * 100)
            if height_cm > 0:
                return height_cm
        if self.hoehe is not None:
            match = re.match(r'(\d+)[,.](\d+)\s*m', self.hoehe)
            if match:
                meters = Decimal(f'{match.group(1)}.{match.group(2)}')
                height_cm = int(meters * 100)
                if height_cm > 0:
                    return height_cm
        return None

    def _get_park_and_ride_type(self) -> list[ParkAndRideType]:
        if self.oeffi == 'J':
            return [ParkAndRideType.YES]
        if self.oeffi == 'N':
            return [ParkAndRideType.NO]
        return []

    def _get_opening_hours(self) -> str | None:
        if not self.oeff_mo_fr and not self.oeff_sa and not self.oeff_so:
            return None

        if self.oeff_mo_fr == 'durchgehend' and self.oeff_sa == 'durchgehend' and self.oeff_so == 'durchgehend':
            return '24/7'

        time_range_pattern = re.compile(r'^\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}$')
        parts: list[str] = []

        if self.oeff_mo_fr and time_range_pattern.match(self.oeff_mo_fr):
            parts.append(f'Mo-Fr {self.oeff_mo_fr}')
        elif self.oeff_mo_fr == 'durchgehend':
            parts.append('Mo-Fr 00:00-24:00')
        elif self.oeff_mo_fr:
            return None

        if self.oeff_sa and time_range_pattern.match(self.oeff_sa):
            parts.append(f'Sa {self.oeff_sa}')
        elif self.oeff_sa == 'durchgehend':
            parts.append('Sa 00:00-24:00')
        elif self.oeff_sa:
            return None

        if self.oeff_so and time_range_pattern.match(self.oeff_so):
            parts.append(f'Su {self.oeff_so}')
        elif self.oeff_so == 'durchgehend':
            parts.append('Su 00:00-24:00')
        elif self.oeff_so:
            return None

        if not parts:
            return None

        return '; '.join(parts)

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        lat, lon = self._parse_wkt_coordinates()

        return StaticParkingSiteInput(
            uid=self.gid,
            name=self.bez,
            lat=lat,
            lon=lon,
            type=self.typ.to_parking_site_type(),
            capacity=self.kapazitaet if self.kapazitaet is not None else 0,
            address=self.zufahrt,
            description=self.kategorie,
            max_height=self._get_max_height(),
            has_fee=self.gebuehren,
            fee_description=self.gebuehren_internet,
            park_and_ride_type=self._get_park_and_ride_type(),
            opening_hours=self._get_opening_hours(),
            purpose=PurposeType.CAR,
            has_realtime_data=False,
            static_data_updated_at=datetime.now(tz=timezone.utc),
        )
