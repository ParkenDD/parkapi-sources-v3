"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum

import shapely
from shapely import GeometryType
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon
from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, EnumValidator, IntegerValidator, Noneable, StringValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import EmptystringNoneable, GeoJSONGeometryValidator


class ArtProperty(Enum):
    STANDS_SINGLE_SIDE = 'Anlehnbügel einseitig'
    STANDS_BOTH_SIDE = 'Anlehnbügel beidseitig'
    WALL_LOOPS = 'Vorderradhalter'
    SAFE_WALL_LOOPS = 'Vorderrad-Rahmenhalter'
    FLOOR = 'Markierte Fläche'
    LOCKERS = 'Fahrradbox'
    SHED = 'Sammelschließanlage'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        return {
            self.STANDS_SINGLE_SIDE: ParkingSiteType.STANDS,
            self.STANDS_BOTH_SIDE: ParkingSiteType.STANDS,
            self.WALL_LOOPS: ParkingSiteType.WALL_LOOPS,
            self.SAFE_WALL_LOOPS: ParkingSiteType.SAFE_WALL_LOOPS,
            self.FLOOR: ParkingSiteType.FLOOR,
            self.LOCKERS: ParkingSiteType.LOCKERS,
            self.SHED: ParkingSiteType.SHED,
        }.get(self)


class UeberdachungProperty(Enum):
    true = 1  # roof available
    false = 0  # roof not available


class BeleuchtungProperty(Enum):
    true = 1  # lighting available
    false = 0  # lighting not available


@validataclass
class KonstanzProperty:
    OBJECTID: int = IntegerValidator()
    Lagebezeichnung: str | None = StringValidator()
    Art: ArtProperty = EnumValidator(ArtProperty)
    Ueberdachung: EnumValidator[UeberdachungProperty] | None = Noneable(EnumValidator(UeberdachungProperty))
    Beleuchtung: EnumValidator[BeleuchtungProperty] | None = Noneable(EnumValidator(BeleuchtungProperty))
    Kapazitaet: int = IntegerValidator(min_value=1, allow_strings=True)
    Stadtteil: str | None = EmptystringNoneable(StringValidator())
    Anmerkung: str | None = EmptystringNoneable(StringValidator())
    Eigentuemer_Baulasttraeger: str | None = EmptystringNoneable(StringValidator())


@validataclass
class KonstanzBikeParkingSiteInput:
    geometry: Polygon | MultiPolygon = GeoJSONGeometryValidator(
        allowed_geometry_types=[GeometryType.POLYGON, GeometryType.MULTIPOLYGON],
    )
    properties: KonstanzProperty = DataclassValidator(KonstanzProperty)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        center = shapely.centroid(self.geometry)
        name = self.properties.Lagebezeichnung if self.properties.Lagebezeichnung else self.properties.Art.value
        if self.properties.Stadtteil:
            name += ', ' + self.properties.Stadtteil

        static_parking_site_input = StaticParkingSiteInput(
            uid=str(self.properties.OBJECTID),
            name=name,
            type=self.properties.Art.to_parking_site_type_input(),
            is_covered=True if self.properties.Ueberdachung == UeberdachungProperty.true else False,
            has_lighting=True if self.properties.Beleuchtung == BeleuchtungProperty.true else False,
            capacity=self.properties.Kapazitaet,
            lat=round_7d(center.y),
            lon=round_7d(center.x),
            static_data_updated_at=datetime.now(tz=timezone.utc),
            has_realtime_data=False,
        )

        if self.properties.Eigentuemer_Baulasttraeger != 'privat':
            static_parking_site_input.operator_name = self.properties.Eigentuemer_Baulasttraeger
        if self.properties.Anmerkung:
            static_parking_site_input.description = self.properties.Anmerkung

        return static_parking_site_input
