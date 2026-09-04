"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import pyproj
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    BooleanValidator,
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    IntegerValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import GeojsonBaseFeatureInput, ParkingSiteRestrictionInput, StaticParkingSiteInput
from parkapi_sources.models.enums import (
    ParkAndRideType,
    ParkingAudience,
    ParkingSiteType,
    PurposeType,
    SupervisionType,
)
from parkapi_sources.util import round_7d
from parkapi_sources.validators import ExcelNoneable, ReplacingStringValidator


class OrganizationType(Enum):
    GEMEINDE = 'GEMEINDE'
    KREIS = 'KREIS'
    BUNDESLAND = 'BUNDESLAND'


class RadvisSupervisionType(Enum):
    KEINE = 'KEINE'
    UNBEKANNT = 'UNBEKANNT'
    VIDEO = 'VIDEO'

    def to_supervision_type(self) -> Optional[SupervisionType]:
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
            self.UNBEKANNT: 'Unbekannt',
            self.SONSTIGES: 'Sonstiges',
        }.get(self)

    def to_park_and_ride_types(self) -> list[ParkAndRideType]:
        if self is self.BIKE_AND_RIDE:
            return [ParkAndRideType.YES]
        return []


class RadvisParkingSiteType(Enum):
    ANLEHNBUEGEL = 'ANLEHNBUEGEL'
    FAHRRADBOX = 'FAHRRADBOX'
    VORDERRADANSCHLUSS = 'VORDERRADANSCHLUSS'
    VORDERRADANSCHLUSS_SICHERUNGSBUEGEL = 'VORDERRADANSCHLUSS_SICHERUNGSBUEGEL'
    DOPPELSTOECKIG = 'DOPPELSTOECKIG'
    FAHRRADPARKHAUS = 'FAHRRADPARKHAUS'
    SAMMELANLAGE = 'SAMMELANLAGE'
    SCHLIESSFACH = 'SCHLIESSFACH'
    ABSTELLFLAECHE = 'ABSTELLFLAECHE'
    SONSTIGE = 'SONSTIGE'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.ANLEHNBUEGEL: ParkingSiteType.STANDS,
            self.FAHRRADBOX: ParkingSiteType.LOCKERS,
            self.VORDERRADANSCHLUSS: ParkingSiteType.WALL_LOOPS,
            self.VORDERRADANSCHLUSS_SICHERUNGSBUEGEL: ParkingSiteType.SAFE_WALL_LOOPS,
            self.DOPPELSTOECKIG: ParkingSiteType.TWO_TIER,
            self.FAHRRADPARKHAUS: ParkingSiteType.BUILDING,
            self.SAMMELANLAGE: ParkingSiteType.SHED,
            self.SCHLIESSFACH: ParkingSiteType.LOCKBOX,
            self.ABSTELLFLAECHE: ParkingSiteType.FLOOR,
        }.get(self, ParkingSiteType.OTHER)

    def to_purpose_type(self) -> PurposeType:
        if self is self.SCHLIESSFACH:
            return PurposeType.ITEM
        return PurposeType.BIKE


class StatusType(Enum):
    AKTIV = 'AKTIV'
    GEPLANT = 'GEPLANT'
    AUSSER_BETRIEB = 'AUSSER_BETRIEB'


@validataclass
class RadvisFeaturePropertiesInput:
    id: int = IntegerValidator()
    name: Optional[str] = ExcelNoneable(StringValidator(max_length=256)), Default(None)
    betreiber: Optional[str] = ExcelNoneable(StringValidator(max_length=256)), Default(None)
    quell_system: str = StringValidator()
    externe_id: Optional[str] = ExcelNoneable(StringValidator()), Default(None)
    zustaendig: Optional[str] = ExcelNoneable(StringValidator()), Default(None)
    # Use ExcelNoneable because zustaendig_orga_typ can be emptystring
    zustaendig_orga_typ: Optional[OrganizationType] = ExcelNoneable(EnumValidator(OrganizationType)), Default(None)
    kapazitaet: int = IntegerValidator(min_value=0)
    kapazitaet_lastenraeder: Optional[int] = ExcelNoneable(IntegerValidator(min_value=0)), Default(None)
    anzahl_lademoeglichkeiten: Optional[int] = ExcelNoneable(IntegerValidator(min_value=0)), Default(None)
    ueberwacht: RadvisSupervisionType = EnumValidator(RadvisSupervisionType)
    abstellanlagen_ort: LocationType = EnumValidator(LocationType)
    groessenklasse: Optional[str] = ExcelNoneable(StringValidator()), Default(None)
    stellplatzart: RadvisParkingSiteType = EnumValidator(RadvisParkingSiteType)
    ueberdacht: bool = BooleanValidator()
    gebuehren_pro_tag: Optional[int] = ExcelNoneable(IntegerValidator()), Default(None)
    gebuehren_pro_monat: Optional[int] = ExcelNoneable(IntegerValidator()), Default(None)
    gebuehren_pro_jahr: Optional[int] = ExcelNoneable(IntegerValidator()), Default(None)
    beschreibung_gebuehren: Optional[str] = (
        ExcelNoneable(ReplacingStringValidator(max_length=4096, mapping={'\n': ' ', '\r': ''})),
        Default(None),
    )
    beschreibung: Optional[str] = (
        ExcelNoneable(ReplacingStringValidator(max_length=4096, mapping={'\x80': ' ', '\n': ' ', '\r': ''})),
        Default(None),
    )
    weitere_information: Optional[str] = (
        ExcelNoneable(ReplacingStringValidator(max_length=4096, mapping={'\n': ' ', '\r': ''})),
        Default(None),
    )
    photo_url: Optional[str] = ExcelNoneable(UrlValidator(max_length=4096)), Default(None)
    zuletzt_bearbeitet_am: datetime = DateTimeValidator(
        local_timezone=timezone.utc,
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )
    status: StatusType = EnumValidator(StatusType)

    @property
    def description(self) -> Optional[str]:
        if self.beschreibung and self.weitere_information:
            return f'{self.beschreibung} {self.weitere_information}'
        return self.beschreibung or self.weitere_information

    @property
    def has_fee(self) -> Optional[bool]:
        fees = [
            fee
            for fee in [self.gebuehren_pro_tag, self.gebuehren_pro_monat, self.gebuehren_pro_jahr]
            if fee is not None
        ]
        if not fees:
            return None

        # A fee of 0 means that the parking site is free of charge, so just a fee which is set and not 0 is a fee.
        return any(fee != 0 for fee in fees)

    @property
    def restrictions(self) -> list[ParkingSiteRestrictionInput]:
        restrictions: list[ParkingSiteRestrictionInput] = []

        if self.anzahl_lademoeglichkeiten:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                    capacity=self.anzahl_lademoeglichkeiten,
                ),
            )

        if self.kapazitaet_lastenraeder:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CARGOBIKE,
                    capacity=self.kapazitaet_lastenraeder,
                ),
            )

        return restrictions

    def to_dict(self) -> dict:
        return {
            'uid': str(self.id),
            'name': self.name or 'Abstellanlage',
            'operator_name': self.betreiber,
            'type': self.stellplatzart.to_parking_site_type(),
            'purpose': self.stellplatzart.to_purpose_type(),
            'capacity': self.kapazitaet,
            'restrictions': self.restrictions,
            'description': self.description,
            'photo_url': self.photo_url,
            'has_realtime_data': False,
            'is_covered': self.ueberdacht,
            'has_fee': self.has_fee,
            'fee_description': self.beschreibung_gebuehren,
            'related_location': self.abstellanlagen_ort.to_related_location(),
            'park_and_ride_type': self.abstellanlagen_ort.to_park_and_ride_types(),
            'supervision_type': self.ueberwacht.to_supervision_type(),
            'tags': [f'BW_SIZE_{self.groessenklasse}'] if self.groessenklasse else [],
            'static_data_updated_at': self.zuletzt_bearbeitet_am,
        }


@validataclass
class RadvisFeatureInput(GeojsonBaseFeatureInput):
    properties: RadvisFeaturePropertiesInput = DataclassValidator(RadvisFeaturePropertiesInput)

    def to_static_parking_site_input_with_proj(self, proj: pyproj.Proj) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            **self.properties.to_dict(),
        )

        coordinates = proj(float(static_parking_site_input.lon), float(static_parking_site_input.lat), inverse=True)
        static_parking_site_input.lon = round_7d(coordinates[0])
        static_parking_site_input.lat = round_7d(coordinates[1])

        return static_parking_site_input
