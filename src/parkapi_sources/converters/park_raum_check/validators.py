"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from enum import Enum
from typing import Any

import shapely
from isodate import Duration
from pyproj import Transformer
from shapely import GeometryType, LineString
from shapely.geometry.polygon import Polygon
from validataclass.dataclasses import ValidataclassMixin, validataclass
from validataclass.validators import (
    BooleanValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import (
    ExternalIdentifierInput,
    ExternalIdentifierType,
    ParkAndRideType,
    ParkingAudience,
    ParkingSiteRestrictionInput,
    ParkingSiteType,
    PurposeType,
    StaticParkingSiteInput,
)
from parkapi_sources.models.enums import ParkingSiteOrientation
from parkapi_sources.util import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator, ReplacingStringValidator


class SachsenheimDedication(Enum):
    PUBLIC = 'öffentlich'
    PRIVATE = 'privat'  # Ignored in converter, as all data is missing
    DISABLED = 'behinderten Stellplatz'
    CHARGING_1 = 'Lademöglichkeit'
    CHARGING_2 = 'E-Ladesäule'


class SachsenheimParkingOrientation(Enum):
    DIAGONAL = 'Schrägparken'
    PARALLEL = 'Längsparken'
    PERPENDICULAR_1 = 'Senkrechtparken'
    PERPENDICULAR_2 = 'Querparken'
    NONE = 'Keine'

    def to_parking_side_orientation(self) -> ParkingSiteOrientation | None:
        return {
            self.DIAGONAL: ParkingSiteOrientation.DIAGONAL,
            self.PARALLEL: ParkingSiteOrientation.PARALLEL,
            self.PERPENDICULAR_1: ParkingSiteOrientation.PERPENDICULAR,
            self.PERPENDICULAR_2: ParkingSiteOrientation.PERPENDICULAR,
        }.get(self)


class SachsenheimLocation(Enum):
    PARK_AND_RIDE = 'P+R'
    PARKING_SPACE = 'Parkplatz'
    ON_STREET = 'Straßenraum'
    TRAIN_STATION = 'Bahnhof'
    CAR_PARK = 'Parkhaus'
    PARKING_DECK = 'Parkdeck'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.PARK_AND_RIDE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.PARKING_SPACE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.ON_STREET: ParkingSiteType.ON_STREET,
            self.TRAIN_STATION: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
            self.PARKING_DECK: ParkingSiteType.CAR_PARK,
        }.get(self)


class ParkingManagementType(Enum):
    FREE_PARKING = 'Freies Parken'
    PARKING_DISC = 'Parkscheibe'
    DISABLED = 'Behindertenparkplatz'
    CHARGING = 'E-Ladesäule'
    PARKING_TICKET = 'Parkschein'
    HALF_PUBLIC = 'Halböffentlich'


def normalize_key(key: str) -> str:
    key = key.lower().replace(' ', '_').replace('-', '_').replace('.', '')
    return key.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')


@validataclass
class ParkRaumCheckPropertiesInput(ValidataclassMixin):
    fid: int = IntegerValidator()
    name: str = StringValidator()
    adresse: str = StringValidator()
    ort: str = StringValidator()
    widmung: SachsenheimDedication = EnumValidator(SachsenheimDedication)
    parkrichtung: SachsenheimParkingOrientation | None = Noneable(EnumValidator(SachsenheimParkingOrientation))
    ortsbezug: SachsenheimLocation = EnumValidator(SachsenheimLocation)
    haltestellen_id: str | None = Noneable(StringValidator())
    gebuehrenpflichtig: bool = BooleanValidator()
    gebuehreninformation: str | None = Noneable(StringValidator())
    bewirtschaftung: ParkingManagementType | None = Noneable(EnumValidator(ParkingManagementType))
    maximale_parkdauer: int | None = Noneable(IntegerValidator(allow_strings=True))
    kapazitaet: int = IntegerValidator()
    kommentar: str | None = Noneable(StringValidator())

    def to_to_static_parking_site_dict(self) -> dict[str, Any]:
        restrictions: list[ParkingSiteRestrictionInput] = []
        if self.bewirtschaftung == ParkingManagementType.DISABLED:
            restrictions.append(ParkingSiteRestrictionInput(type=ParkingAudience.DISABLED, capacity=self.kapazitaet))
        elif self.bewirtschaftung == ParkingManagementType.CHARGING:
            restrictions.append(ParkingSiteRestrictionInput(type=ParkingAudience.CHARGING, capacity=self.kapazitaet))
        if self.maximale_parkdauer:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    max_stay=Duration(minutes=self.maximale_parkdauer),
                ),
            )

        result: dict[str, Any] = {
            'uid': str(self.fid),
            'has_realtime_data': False,
            'name': self.name,
            'address': f'{self.adresse}, {self.ort}',
            'capacity': self.kapazitaet,
            'restrictions': restrictions,
            'has_fee': self.gebuehrenpflichtig,
            'fee_description': self.gebuehreninformation,
            'orientation': None if self.parkrichtung is None else self.parkrichtung.to_parking_side_orientation(),
            'type': self.ortsbezug.to_parking_site_type(),
            'description': self.kommentar,
        }

        if self.ortsbezug == SachsenheimLocation.PARK_AND_RIDE:
            result['park_and_ride_type'] = [ParkAndRideType.YES]

        if self.haltestellen_id:
            result['external_identifiers'] = [
                ExternalIdentifierInput(
                    type=ExternalIdentifierType.DHID,
                    value=self.haltestellen_id,
                ),
            ]

        return result

    @staticmethod
    def __pre_validate__(input_data: dict[Any, Any]) -> dict[Any, Any]:
        return {normalize_key(key): value for key, value in input_data.items()}


@validataclass
class SachsenheimPropertiesInput(ParkRaumCheckPropertiesInput):
    name: str = ReplacingStringValidator(mapping={'\n': ': '})


@validataclass
class KehlPropertiesInput(ParkRaumCheckPropertiesInput):
    name: str = Noneable(StringValidator(), default='Parkplatz')
    maximale_parkdauer: int | None = Noneable(IntegerValidator(allow_strings=True))

    @staticmethod
    def __pre_validate__(input_data: dict[Any, Any]) -> dict[Any, Any]:
        result = {normalize_key(key): value for key, value in input_data.items()}
        result['maximale_parkdauer'] = result.get('max_parkdauer')

        # Remove whitespace at Parkrichtung
        if isinstance(result.get('parkrichtung'), str):
            result['parkrichtung'] = result['parkrichtung'].strip()

        return result


@validataclass
class ParkRaumCheckBaseFeatureInput:
    geometry: LineString = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.LINESTRING])
    properties: ParkRaumCheckPropertiesInput = DataclassValidator(ParkRaumCheckPropertiesInput)

    def to_static_parking_site(
        self,
        static_data_updated_at: datetime,
        transformer: Transformer | None = None,
    ) -> StaticParkingSiteInput:
        if transformer:
            geometry = shapely.transform(self.geometry, transformer.transform, interleaved=False)
        else:
            geometry = self.geometry

        center = shapely.centroid(geometry)

        return StaticParkingSiteInput(
            purpose=PurposeType.CAR,
            lat=round_7d(center.y),
            lon=round_7d(center.x),
            static_data_updated_at=static_data_updated_at,
            **self.properties.to_to_static_parking_site_dict(),
        )


@validataclass
class SachsenheimOnStreetFeatureInput(ParkRaumCheckBaseFeatureInput):
    properties: SachsenheimPropertiesInput = DataclassValidator(SachsenheimPropertiesInput)


@validataclass
class SachsenheimOffStreetFeatureInput(ParkRaumCheckBaseFeatureInput):
    properties: SachsenheimPropertiesInput = DataclassValidator(SachsenheimPropertiesInput)
    geometry: Polygon = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POLYGON])


@validataclass
class KehlFeatureInput(ParkRaumCheckBaseFeatureInput):
    properties: SachsenheimPropertiesInput = DataclassValidator(KehlPropertiesInput)
