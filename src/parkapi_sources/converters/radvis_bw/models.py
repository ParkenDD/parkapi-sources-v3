"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

import pyproj
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    BooleanValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import GeojsonBaseFeatureInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType, SupervisionType
from parkapi_sources.validators import ExcelNoneable, ReplacingStringValidator


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
    BILDUNGSEINRICHTUNG = 'BILDUNGSEINRICHTUNG'

    def to_related_location(self) -> Optional[str]:
        return {
            self.OEFFENTLICHE_EINRICHTUNG: 'Öffentliche Einrichtung',
            self.BIKE_AND_RIDE: 'Bike and Ride',
            self.SCHULE: 'Schule',
            self.STRASSENRAUM: 'Straßenraum',
            self.BILDUNGSEINRICHTUNG: 'Bildungseinrichtung',
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
        }.get(self, ParkingSiteType.OTHER)


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
    beschreibung: Optional[str] = (
        Noneable(ReplacingStringValidator(mapping={'\x80': ' ', '\n': ' ', '\r': ''})),
        Default(None),
    )
    weitere_information: Optional[str] = (
        Noneable(ReplacingStringValidator(mapping={'\n': ' ', '\r': ''})),
        Default(None),
    )
    status: StatusType = EnumValidator(StatusType)

    def to_dicts(self) -> list[dict]:
        description: Optional[str] = None
        if self.beschreibung and self.weitere_information:
            description = f'{self.beschreibung} {self.weitere_information}'
        elif self.beschreibung:
            description = self.beschreibung
        elif self.weitere_information:
            description = self.weitere_information

        base_data = {
            'operator_name': self.betreiber,
            'description': description,
            'has_realtime_data': False,
            'is_covered': self.ueberdacht,
            'related_location': self.abstellanlagen_ort.to_related_location(),
            'supervision_type': self.ueberwacht.to_supervision_type(),
            'tags': [f'BW_SIZE_{self.groessenklasse}'] if self.groessenklasse else [],
            'static_data_updated_at': datetime.now(tz=timezone.utc),
        }

        results: list[dict] = [
            {
                'uid': str(self.id),
                'name': 'Abstellanlage',
                'type': self.stellplatzart.to_parking_site_type(),
                'capacity': self.anzahl_stellplaetze,
                'capacity_charging': self.anzahl_lademoeglichkeiten,
                'purpose': PurposeType.BIKE,
                **base_data,
            },
        ]
        if self.anzahl_schliessfaecher:
            results[0]['group_uid'] = str(self.id)
            results.append({
                'uid': f'{self.id}-lockbox',
                'group_uid': str(self.id),
                'name': 'Schliessfach',
                'type': ParkingSiteType.LOCKBOX,
                'capacity': self.anzahl_schliessfaecher,
                'purpose': PurposeType.ITEM,
                **base_data,
            })
        return results


@validataclass
class RadvisFeatureInput(GeojsonBaseFeatureInput):
    properties: RadvisFeaturePropertiesInput = DataclassValidator(RadvisFeaturePropertiesInput)

    def to_static_parking_site_inputs_with_proj(self, proj: pyproj.Proj) -> list[StaticParkingSiteInput]:
        property_dicts: list[dict] = self.properties.to_dicts()
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        for property_dict in property_dicts:
            static_parking_site_input = StaticParkingSiteInput(
                lat=self.geometry.coordinates[1],
                lon=self.geometry.coordinates[0],
                **property_dict,
            )

            coordinates = proj(float(static_parking_site_input.lon), float(static_parking_site_input.lat), inverse=True)
            static_parking_site_input.lon = Decimal(coordinates[0]).quantize(Decimal('1.0000000'))
            static_parking_site_input.lat = Decimal(coordinates[1]).quantize(Decimal('1.0000000'))

            static_parking_site_inputs.append(static_parking_site_input)

        return static_parking_site_inputs
