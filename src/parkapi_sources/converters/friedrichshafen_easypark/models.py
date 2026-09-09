"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

import shapely
from shapely import GeometryType, LineString
from validataclass.dataclasses import validataclass
from validataclass.validators import EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.converters.friedrichshafen_easypark.validation import StrippedEnumValidator
from parkapi_sources.models import ParkingSiteRestrictionInput, PurposeType, StaticParkingSiteInput
from parkapi_sources.models.enums import (
    LinearParkingPosition,
    ParkingAudience,
    ParkingSiteOrientation,
    ParkingSiteSide,
    ParkingSiteType,
)
from parkapi_sources.util import round_7d
from parkapi_sources.validators import ExcelNoneable, GermanDecimalValidator
from parkapi_sources.validators.csv_geojson_geometry_validator import CsvGeoJSONGeometryValidator


class FriedrichshafenParkingSiteOrientation(Enum):
    PARALLEL = 'PARALLEL'
    DIAGONAL = 'DIAGONAL'
    PERPENDICULAR = 'PERPENDICULAR'
    NO_PARKING = 'NO_PARKING'


class FriedrichshafenPermissionsTranslation(Enum):
    GEBUEHRENPFLICHTIGES_PARKEN_BEWOHNERPARKEN = 'Gebührenpflichtiges Parken/Bewohnerparken'
    GEBUEHRENPFLICHTIGES_PARKEN = 'Gebührenpflichtiges Parken'
    GEBUEHRENFREIES_PARKEN = 'Gebührenfreies Parken'
    PARKEN_MIT_PARKSCHEIBE_BEWOHNERPARKEN = 'Parken mit Parkscheibe/Bewohnerparken'
    PARKEN_MIT_PARKSCHEIBE = 'Parken mit Parkscheibe'
    BEWOHNERPARKEN = 'Bewohnerparken'
    BEHINDERTENPARKPLAETZE = 'Behindertenparkplätze'
    CARSHARING = 'Carsharing'
    E_PARKPLATZ = 'E-Parkplatz'
    LADEZONE = 'Ladezone'
    BUSPARKPLATZ = 'Busparkplatz'
    FAHRRADPARKPLATZ = 'Fahrradparkplatz'
    FAHRRADPARKPLATZ_E_SCOOTER = 'Fahrradparkplatz/E-Scooter'
    FEUERWEHRZUFAHRT = 'Feuerwehrzufahrt'

    def to_parking_audience(self) -> ParkingAudience | None:
        return {
            self.GEBUEHRENPFLICHTIGES_PARKEN_BEWOHNERPARKEN: ParkingAudience.RESIDENT,
            self.PARKEN_MIT_PARKSCHEIBE_BEWOHNERPARKEN: ParkingAudience.RESIDENT,
            self.BEWOHNERPARKEN: ParkingAudience.RESIDENT,
            self.BEHINDERTENPARKPLAETZE: ParkingAudience.DISABLED,
            self.CARSHARING: ParkingAudience.CARSHARING,
            self.E_PARKPLATZ: ParkingAudience.CHARGING,
            self.LADEZONE: ParkingAudience.DELIVERY,
            self.BUSPARKPLATZ: ParkingAudience.BUS,
        }.get(self)

    def has_fee(self) -> bool:
        return self in [
            self.GEBUEHRENPFLICHTIGES_PARKEN_BEWOHNERPARKEN,
            self.GEBUEHRENPFLICHTIGES_PARKEN,
        ]

    def is_no_car_parking(self) -> bool:
        """
        These values are used for areas which are no car parking sites at all, therefore they are not integrated.
        """
        return self in [
            self.FAHRRADPARKPLATZ,
            self.FAHRRADPARKPLATZ_E_SCOOTER,
            self.FEUERWEHRZUFAHRT,
        ]


@validataclass
class FriedrichshafenEasyParkRowInput:
    id: int = IntegerValidator(allow_strings=True)
    length: Decimal = GermanDecimalValidator()
    park_angle: FriedrichshafenParkingSiteOrientation = EnumValidator(FriedrichshafenParkingSiteOrientation)
    street_side: ParkingSiteSide = EnumValidator(ParkingSiteSide)
    location_on_sidewalk: LineString = CsvGeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.LINESTRING])
    permissions_translation: FriedrichshafenPermissionsTranslation = StrippedEnumValidator(
        FriedrichshafenPermissionsTranslation
    )
    permission_period: str | None = ExcelNoneable(StringValidator())
    time_limited: str | None = ExcelNoneable(StringValidator())

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        center = shapely.centroid(self.location_on_sidewalk)

        return StaticParkingSiteInput(
            uid=str(self.id),
            type=ParkingSiteType.ON_STREET,
            linear_parking_position=LinearParkingPosition.PARKING_CENTER_LINE,
            capacity=self._get_capacity(),
            orientation=ParkingSiteOrientation[self.park_angle.name],
            name='Straßenparkplatz',
            purpose=PurposeType.CAR,
            side=self.street_side,
            description=self.permissions_translation.value,
            fee_description=self._get_fee_description(),
            has_realtime_data=False,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            lon=round_7d(center.x),
            lat=round_7d(center.y),
            geojson=self.location_on_sidewalk,
            has_fee=self._get_has_fee(),
            restrictions=self._get_restrictions(),
        )

    def _get_has_fee(self) -> bool:
        if self.permission_period and 'Gebührenpflichtig' in self.permission_period:
            return True

        return self.permissions_translation.has_fee()

    def _get_restrictions(self) -> list[ParkingSiteRestrictionInput]:
        parking_audience = self.permissions_translation.to_parking_audience()
        if parking_audience is None:
            return []

        return [ParkingSiteRestrictionInput(type=parking_audience)]

    def _get_fee_description(self) -> str:
        fee_description_fragments = [self.permissions_translation.value]
        if self.permission_period:
            fee_description_fragments.append(self.permission_period)
        if self.time_limited:
            fee_description_fragments.append(self.time_limited)

        return '; '.join(fee_description_fragments)

    def _get_capacity(self) -> int:
        if self.park_angle == FriedrichshafenParkingSiteOrientation.PARALLEL:
            return int(self.length / Decimal('5'))
        if self.park_angle == FriedrichshafenParkingSiteOrientation.PERPENDICULAR:
            return int(self.length / Decimal('2.5'))
        if self.park_angle == FriedrichshafenParkingSiteOrientation.DIAGONAL:
            return int(self.length / Decimal('3'))

        # Will never happen as long as FriedrichshafenParkingSiteOrientation does not change
        raise ValueError(f'Unknown orientation: {self.park_angle}')
