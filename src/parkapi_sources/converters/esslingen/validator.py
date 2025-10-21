"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime, time, timezone
from enum import Enum
from typing import Any

import pyproj
import shapely
from shapely import GeometryType, LineString
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnyOfValidator,
    DataclassValidator,
    DateValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import (
    ParkingSiteRestrictionInput,
    PurposeType,
    StaticParkingSiteInput,
)
from parkapi_sources.models.enums import (
    ParkingAudience,
    ParkingSiteOrientation,
    ParkingSiteType,
)
from parkapi_sources.util import round_7d
from parkapi_sources.validators import (
    GeoJSONGeometryValidator,
)


class EsslingenOrientation(Enum):
    PARALLEL = 'längs'
    PERPENDICULAR = 'quer'
    DIAGONAL = 'schräg'
    UNDEFINED = 'undefiniert'
    UNKNOWN = 'unbekannt'
    DIVERSE = 'unterschiedlich'

    def to_parking_side_orientation(self) -> ParkingSiteOrientation | None:
        return {
            self.PARALLEL: ParkingSiteOrientation.PARALLEL,
            self.DIAGONAL: ParkingSiteOrientation.DIAGONAL,
            self.PERPENDICULAR: ParkingSiteOrientation.PERPENDICULAR,
        }.get(self)


@validataclass
class EsslingenParkingSiteInput:
    capacity: int = IntegerValidator()
    Ausrichtung: EsslingenOrientation | None = Noneable(EnumValidator(EsslingenOrientation)), Default(None)
    Bemerkungen: str | None = Noneable(StringValidator()), Default(None)
    other_restrictions: str | None = Noneable(StringValidator()), Default(None)
    fid: int = IntegerValidator()
    free_for_parking_parking_number: str | None = Noneable(StringValidator()), Default(None)
    parking_type: str | None = Noneable(StringValidator()), Default(None)
    allow_time: str | None = Noneable(StringValidator()), Default(None)
    parking_disc_required: str | None = Noneable(StringValidator()), Default(None)
    parking_ticket_required: str | None = Noneable(StringValidator()), Default(None)
    static_data_updated_at: date = DateValidator()

    @staticmethod
    def __pre_validate__(input_data: Any, **kwargs: Any):
        key_mapping: dict[str, str] = {
            'Anzahl der Stellplätze': 'capacity',
            'Beschränkung sonstig': 'other_restrictions',
            'Frei für Parkausweis-Nr': 'free_for_parking_parking_number',
            'Parkerlaubnis zeitlich': 'restriction_time',
            'Parkplatz-Typ': 'parking_type',
            'Parkscheibe erforderlich': 'parking_disc_required',
            'Parkschein erforderlich': 'parking_ticket_required',
            'Überprüfungsdatum': 'static_data_updated_at',
        }

        return {key_mapping.get(key, key): value for key, value in input_data.items()}


@validataclass
class EsslingenParkingSiteFeatureInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: EsslingenParkingSiteInput = DataclassValidator(EsslingenParkingSiteInput)
    geometry: LineString = GeoJSONGeometryValidator(
        allowed_geometry_types=[GeometryType.POLYGON],
        projection=pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True),
    )

    def to_static_parking_site(self) -> StaticParkingSiteInput | None:
        if self.properties.parking_type is None or self.properties.parking_type in [
            'Wanderparkplatz',
            'Privater Parkplatz',
            'Behinderten-Parkplatz privat',
            'Parkplatz für Elektrofahrzeuge während des Ladevorgangs privat',
            'Parkplatz wegen Baustelle zurzeit nicht verfügbar',
            'Parkplatz ungeklärt',
            'Kein Parkplatz',
        ]:
            return None

        center = shapely.centroid(self.geometry)
        description = []
        if self.properties.Bemerkungen:
            description.append(self.properties.Bemerkungen)
        if self.properties.other_restrictions:
            description.append(self.properties.other_restrictions)
        if self.properties.allow_time:
            description.append(f'Parkerlaubnis: {self.properties.allow_time}')
        if self.properties.free_for_parking_parking_number:
            description.append(f'Frei für Parkausweis-Nr {self.properties.free_for_parking_parking_number}')

        static_parking_site_input = StaticParkingSiteInput(
            uid=str(self.properties.fid),
            name=str(self.properties.fid),
            type=ParkingSiteType.ON_STREET,
            lat=round_7d(center.y),
            lon=round_7d(center.x),
            capacity=self.properties.capacity,
            has_fee=self.properties.parking_ticket_required is not None,
            fee_description=', '.join(description) if description else None,
            orientation=self.properties.Ausrichtung.to_parking_side_orientation()
            if self.properties.Ausrichtung
            else None,
            geojson=self.geometry,
            static_data_updated_at=datetime.combine(
                self.properties.static_data_updated_at, time(12), tzinfo=timezone.utc
            ),
            has_realtime_data=False,
        )

        match self.properties.parking_type:
            case 'Bewohner-Parkplatz':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.RESIDENT),
                )
            case 'Behinderten-Parkplatz allgemein':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.DISABLED),
                )
            case 'Behinderten-Parkplatz beschränkt auf bestimmte Zeiten, sonst für die Öffentlichkeit':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.DISABLED),
                )
            case 'Behinderten-Parkplatz beschränkt auf bestimmte Zeiten, sonst nur für Bewohner':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.DISABLED),
                )
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.RESIDENT),
                )
            case 'Behinderten-Parkplatz beschränkt auf bestimmte Zeiten, sonst für Taxi':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.DISABLED),
                )
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.TAXI),
                )
            case 'Behinderten-Parkplatz für bestimmte Parkausweis-Nummer':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.DISABLED),
                )
            case 'Motorrad-Parkplatz':
                static_parking_site_input.purpose = PurposeType.MOTORCYCLE
            case 'Carsharing-Stellplatz':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.CARSHARING),
                )
            case 'Taxi-Stellplatz':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.TAXI),
                )
            case 'Parkplatz für Elektrofahrzeuge während des Ladevorgangs':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.CHARGING),
                )
            case 'Wohnmobil-Parkplatz':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.CARAVAN),
                )
            case 'Omnibus-Parkplatz':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.BUS),
                )
            case 'Lkw-Parkplatz':
                static_parking_site_input.restrictions.append(
                    ParkingSiteRestrictionInput(type=ParkingAudience.TRUCK),
                )
            case 'Parkplatz privat betrieben für die Öffentlichkeit':
                static_parking_site_input.type = ParkingSiteType.OFF_STREET_PARKING_GROUND
            case 'Parkhaus oder Tiefgarage privat betrieben für die Öffentlichkeit':
                static_parking_site_input.type = ParkingSiteType.CAR_PARK

        return static_parking_site_input
