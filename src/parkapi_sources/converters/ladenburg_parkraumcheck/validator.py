"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from enum import Enum
from typing import Any

import shapely
from isodate import Duration
from shapely import GeometryType, LineString
from validataclass.dataclasses import validataclass
from validataclass.validators import (
    AnyOfValidator,
    BooleanValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import (
    ParkingAudience,
    ParkingSiteRestrictionInput,
    StaticParkingSiteInput,
)
from parkapi_sources.models.enums import ParkingSiteOrientation, ParkingSiteSide, ParkingSiteType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import (
    GeoJSONGeometryValidator,
)


class LadenburgParkraumcheckOrientation(Enum):
    PARALLEL = 'Längsparken'
    PERPENDICULAR = 'Senkrechtparken'
    DIAGONAL = 'Schrägparken'

    def to_parking_side_orientation(self) -> ParkingSiteOrientation:
        return {
            self.PARALLEL: ParkingSiteOrientation.PARALLEL,
            self.DIAGONAL: ParkingSiteOrientation.DIAGONAL,
            self.PERPENDICULAR: ParkingSiteOrientation.PERPENDICULAR,
        }.get(self)


class LadenburgParkraumcheckProperty(Enum):
    FREE_PARKING = 'Freies Parken'
    CHARGING = 'E-Ladesäule'
    PARKING_DISC = 'Parkscheibe'
    DISABLED = 'Behindertenparkplatz'
    CARSHARING = 'Carsharing'
    TAXI = 'Taxi'

    def to_restriction_type(self) -> ParkingAudience | None:
        return {
            self.CHARGING: ParkingAudience.CHARGING,
            self.DISABLED: ParkingAudience.DISABLED,
            self.CARSHARING: ParkingAudience.CARSHARING,
            self.TAXI: ParkingAudience.TAXI,
        }.get(self)


class HeidelbergEasyparkSide(Enum):
    RIGHT = 'rechts'
    LEFT = 'links'

    def to_parking_site_side(self) -> ParkingSiteSide:
        return {
            self.RIGHT: ParkingSiteSide.RIGHT,
            self.LEFT: ParkingSiteSide.LEFT,
        }.get(self)


@validataclass
class LadenburgParkraumcheckPropertiesInput:
    fid: int = IntegerValidator()
    Adresse: str = StringValidator()
    Ort: str = StringValidator()
    Parkrichtung: LadenburgParkraumcheckOrientation = EnumValidator(LadenburgParkraumcheckOrientation)
    Gebuehreninformation: str | None = Noneable(StringValidator())
    Bewirtschaftung: LadenburgParkraumcheckProperty = EnumValidator(LadenburgParkraumcheckProperty)
    Maximale_Parkdauer: int | None = Noneable(IntegerValidator())
    Kapazitaet: int = IntegerValidator()
    Kommentar: str | None = Noneable(StringValidator())
    Gebuehrenpflichtig: bool = BooleanValidator()

    @staticmethod
    def __pre_validate__(input_data: Any, **kwargs):
        return {key.replace('ä', 'ae').replace('ü', 'ue'): value for key, value in input_data.items()}


@validataclass
class LadenburgParkraumcheckParkingSiteInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: LadenburgParkraumcheckPropertiesInput = DataclassValidator(LadenburgParkraumcheckPropertiesInput)
    geometry: LineString = GeoJSONGeometryValidator(
        allowed_geometry_types=[GeometryType.LINESTRING],
    )

    def to_static_parking_site(self, static_data_updated_at: datetime) -> StaticParkingSiteInput | None:
        center = shapely.centroid(self.geometry)

        description = self.properties.Kommentar or ''
        description = description.replace('Zum Erhebungszeitpunkt Baustelle" will be removed', '').strip()
        if self.properties.Gebuehreninformation:
            description = f'{description}, Bewirtschaftung: {self.properties.Gebuehreninformation}'

        parking_restriction: ParkingSiteRestrictionInput | None = None
        if self.properties.Maximale_Parkdauer or self.properties.Bewirtschaftung.to_restriction_type():
            parking_restriction = ParkingSiteRestrictionInput()
            if self.properties.Maximale_Parkdauer:
                parking_restriction.max_stay = Duration(minutes=self.properties.Maximale_Parkdauer)
            if self.properties.Bewirtschaftung.to_restriction_type():
                parking_restriction.type = self.properties.Bewirtschaftung.to_restriction_type()

        return StaticParkingSiteInput(
            uid=str(self.properties.fid),
            name=self.properties.Adresse,
            address=f'{self.properties.Adresse}, {self.properties.Ort}',
            static_data_updated_at=static_data_updated_at,
            type=ParkingSiteType.ON_STREET,
            lat=round_7d(center.y),
            lon=round_7d(center.x),
            capacity=self.properties.Kapazitaet,
            has_fee=self.properties.Gebuehrenpflichtig,
            description=description or None,
            orientation=self.properties.Parkrichtung.to_parking_side_orientation(),
            geojson=self.geometry,
            has_realtime_data=False,
            restrictions=[] if parking_restriction is None else [parking_restriction],
        )
