"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

import pyproj
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import BooleanValidator, DataclassValidator, EnumValidator, IntegerValidator, Noneable, StringValidator

from parkapi_sources.converters.base_converter.pull.static_geojson_data_mixin.models import GeojsonFeatureInput
from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, SupervisionType
from parkapi_sources.validators import ExcelNoneable


class OrganizationType(Enum):
    GEMEINDE = 'GEMEINDE'
    KREIS = 'KREIS'


class RadvisSupervisionType(Enum):
    KEINE = 'KEINE'
    UNBEKANNT = 'UNBEKANNT'
    VIDEO = 'VIDEO'

    def to_supervision_type(self) -> SupervisionType:
        return {
            self.KEINE: SupervisionType.NO,
            self.VIDEO: SupervisionType.VIDEO,
        }.get(self)


class LocationType(Enum):
    OEFFENTLICHE_EINRICHTUNG = 'OEFFENTLICHE_EINRICHTUNG'
    BIKE_AND_RIDE = 'BIKE_AND_RIDE'
    UNBEKANNT = 'UNBEKANNT'
    SCHULE = 'SCHULE'
    STRASSENRAUM = 'STRASSENRAUM'
    SONSTIGES = 'SONSTIGES'

    def to_related_location(self) -> Optional[str]:
        return {
            self.OEFFENTLICHE_EINRICHTUNG: 'Öffentliche Einrichtung',
            self.BIKE_AND_RIDE: 'Bike and Ride',
            self.SCHULE: 'Schule',
            self.STRASSENRAUM: 'Straßenraum',
        }.get(self)


class RadvisParkingSiteType(Enum):
    ANLEHNBUEGEL = 'ANLEHNBUEGEL'
    FAHRRADBOX = 'FAHRRADBOX'
    VORDERRADANSCHLUSS = 'VORDERRADANSCHLUSS'
    SONSTIGE = 'SONSTIGE'
    DOPPELSTOECKIG = 'DOPPELSTOECKIG'
    FAHRRADPARKHAUS = 'FAHRRADPARKHAUS'
    SAMMELANLAGE = 'SAMMELANLAGE'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.ANLEHNBUEGEL: ParkingSiteType.STANDS,
            self.FAHRRADBOX: ParkingSiteType.LOCKERS,
            self.VORDERRADANSCHLUSS: ParkingSiteType.WALL_LOOPS,
            self.DOPPELSTOECKIG: ParkingSiteType.TWO_TIER,
            self.FAHRRADPARKHAUS: ParkingSiteType.BUILDING,
            self.SAMMELANLAGE: ParkingSiteType.SHED,
        }.get(self, ParkingSiteType.GENERIC_BIKE)


class StatusType(Enum):
    AKTIV = 'AKTIV'


@validataclass
class RadvisFeaturePropertiesInput:
    id: int = IntegerValidator()
    betreiber: str = StringValidator()
    quell_system: str = StringValidator()
    externe_id: Optional[str] = Noneable(StringValidator())
    zustaendig: Optional[str] = Noneable(StringValidator())
    # Use ExcelNoneable because zustaendig_orga_typ can be emptystring
    zustaendig_orga_typ: Optional[OrganizationType] = ExcelNoneable(EnumValidator(OrganizationType))
    anzahl_stellplaetze: int = IntegerValidator()
    anzahl_schliessfaecher: Optional[int] = Noneable(IntegerValidator())
    anzahl_lademoeglichkeiten: Optional[int] = Noneable(IntegerValidator())
    ueberwacht: RadvisSupervisionType = EnumValidator(RadvisSupervisionType)
    abstellanlagen_ort: LocationType = EnumValidator(LocationType)
    groessenklasse: Optional[str] = Noneable(StringValidator())
    stellplatzart: RadvisParkingSiteType = EnumValidator(RadvisParkingSiteType)
    ueberdacht: bool = BooleanValidator()
    gebuehren_pro_tag: Optional[int] = Noneable(IntegerValidator())
    gebuehren_pro_monat: Optional[int] = Noneable(IntegerValidator())
    gebuehren_pro_jahr: Optional[int] = Noneable(IntegerValidator())
    beschreibung: Optional[str] = Noneable(StringValidator(multiline=True)), Default(None)
    weitere_information: Optional[str] = Noneable(StringValidator(multiline=True)), Default(None)
    status: StatusType = EnumValidator(StatusType)

    def to_dict(self) -> dict:
        description: Optional[str] = None
        if self.beschreibung and self.weitere_information:
            description = f'{self.beschreibung} {self.weitere_information}'
        elif self.beschreibung:
            description = self.beschreibung
        elif self.weitere_information:
            description = self.weitere_information
        if description is not None:
            description = description.replace('\r', '').replace('\n', ' ')

        return {
            'uid': str(self.id),
            'name': 'Abstellanlage',
            'operator_name': self.betreiber,
            'type': self.stellplatzart.to_parking_site_type(),
            'description': description,
            'has_realtime_data': False,
            'is_covered': self.ueberdacht,
            'supervision_type': self.ueberwacht.to_supervision_type(),
            'capacity': self.anzahl_stellplaetze,
            'capacity_charging': self.anzahl_lademoeglichkeiten,
            'related_location': self.abstellanlagen_ort.to_related_location(),
            'tags': [f'BW_SIZE_{self.groessenklasse}'] if self.groessenklasse else [],
        }


@validataclass
class RadvisFeatureInput(GeojsonFeatureInput):
    properties: RadvisFeaturePropertiesInput = DataclassValidator(RadvisFeaturePropertiesInput)

    def to_static_parking_site_input_with_proj(self, static_data_updated_at: datetime, proj: pyproj.Proj) -> StaticParkingSiteInput:
        result = self.to_static_parking_site_input(static_data_updated_at)

        coordinates = proj(float(result.lon), float(result.lat), inverse=True)
        result.lon = Decimal(coordinates[0]).quantize(Decimal('1.0000000'))
        result.lat = Decimal(coordinates[1]).quantize(Decimal('1.0000000'))

        return result
