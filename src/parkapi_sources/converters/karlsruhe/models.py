"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime, time, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from validataclass.dataclasses import DefaultUnset, validataclass
from validataclass.helpers import OptionalUnset, UnsetValue
from validataclass.validators import (
    DataclassValidator,
    DateTimeValidator,
    EmailValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    NoneToUnsetValue,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.converters.base_converter.pull import GeojsonFeatureGeometryInput
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus, ParkingSiteType, PurposeType
from parkapi_sources.validators import ParsedDateValidator


class KarlsruheOpeningStatus(Enum):
    OPEN = 'Geöffnet'
    CLOSED = 'Geschlossen'

    def to_opening_status(self) -> OpeningStatus:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
        }.get(self, OpeningStatus.UNKNOWN)


@validataclass
class KarlsruhePropertiesInput:
    id: int = IntegerValidator()
    ph_name: str = StringValidator()
    gesamte_parkplaetze: int = IntegerValidator()
    freie_parkplaetze: Optional[int] = Noneable(IntegerValidator())
    max_durchfahrtshoehe: Optional[Decimal] = Noneable(NumericValidator())
    stand_freieparkplaetze: Optional[datetime] = Noneable(DateTimeValidator())
    parkhaus_strasse: str = StringValidator()
    parkhaus_plz: str = StringValidator()
    parkhaus_gemeinde: str = StringValidator()
    oeffnungsstatus: Optional[KarlsruheOpeningStatus] = Noneable(EnumValidator(KarlsruheOpeningStatus))
    bemerkung: Optional[str] = Noneable(StringValidator())
    parkhaus_internet: Optional[str] = Noneable(UrlValidator())
    parkhaus_telefon: Optional[str] = Noneable(StringValidator())
    parkhaus_email: Optional[str] = Noneable(EmailValidator())
    betreiber_internet: Optional[str] = Noneable(UrlValidator())
    betreiber_email: Optional[str] = Noneable(EmailValidator())
    betreiber_telefon: Optional[str] = Noneable(StringValidator())
    stand_parkhausdaten: date = ParsedDateValidator(date_format='%Y-%m-%dZ')

    def __post_init__(self):
        if self.max_durchfahrtshoehe == 0:  # 0 is used as None
            self.max_durchfahrtshoehe = None


@validataclass
class KarlsruheFeatureInput:
    id: str = StringValidator()
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)
    properties: KarlsruhePropertiesInput = DataclassValidator(KarlsruhePropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.properties.id),
            name=self.properties.ph_name,
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            capacity=self.properties.gesamte_parkplaetze,
            address=f'{self.properties.parkhaus_strasse}, {self.properties.parkhaus_plz} {self.properties.parkhaus_gemeinde}',
            max_height=None if self.properties.max_durchfahrtshoehe is None else int(self.properties.max_durchfahrtshoehe * 100),
            public_url=self.properties.parkhaus_internet,
            static_data_updated_at=datetime.combine(self.properties.stand_parkhausdaten, time(), tzinfo=timezone.utc),
            has_realtime_data=True,
        )

    def to_realtime_parking_site_input(self) -> Optional[RealtimeParkingSiteInput]:
        if self.properties.stand_freieparkplaetze is None:
            return None

        if self.properties.oeffnungsstatus is None:
            opening_status = OpeningStatus.UNKNOWN
        else:
            opening_status = self.properties.oeffnungsstatus.to_opening_status()

        return RealtimeParkingSiteInput(
            uid=str(self.properties.id),
            realtime_capacity=self.properties.gesamte_parkplaetze,
            realtime_free_capacity=self.properties.freie_parkplaetze,
            realtime_opening_status=opening_status,
            realtime_data_updated_at=self.properties.stand_freieparkplaetze,
        )


class KarlsruheBikeType(Enum):
    BIKE_BOX = 'Fahrradbox'
    STANDS_WITH_ROOF = 'Fahrradabstellanlage überdacht'
    STANDS = 'Fahrradabstellanlage'
    STATION = 'Fahrradstation'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.BIKE_BOX: ParkingSiteType.LOCKERS,
            self.STANDS: ParkingSiteType.STANDS,
            self.STANDS_WITH_ROOF: ParkingSiteType.SHED,
            self.STATION: ParkingSiteType.BUILDING,
        }.get(self)


@validataclass
class KarlsruheBikePropertiesInput:
    art: KarlsruheBikeType = EnumValidator(KarlsruheBikeType)
    standort: str = StringValidator()
    gemeinde: str = StringValidator()
    stadtteil: OptionalUnset[str] = NoneToUnsetValue(StringValidator()), DefaultUnset
    stellplaetze: int = IntegerValidator(allow_strings=True)
    link: OptionalUnset[str] = NoneToUnsetValue(UrlValidator()), DefaultUnset
    bemerkung: OptionalUnset[str] = NoneToUnsetValue(StringValidator()), DefaultUnset


@validataclass
class KarlsruheBikeFeatureInput:
    id: str = StringValidator()
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)
    properties: KarlsruheBikePropertiesInput = DataclassValidator(KarlsruheBikePropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        address_fragments = [self.properties.standort, self.properties.stadtteil, self.properties.gemeinde]
        address = ', '.join([fragment for fragment in address_fragments if fragment is not UnsetValue])
        return StaticParkingSiteInput(
            uid=str(self.id),
            name=self.properties.standort,
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            capacity=self.properties.stellplaetze,
            address=address,
            public_url=self.properties.link,
            is_covered=self.properties.art == KarlsruheBikeType.STANDS_WITH_ROOF or UnsetValue,
            description=self.properties.bemerkung,
            static_data_updated_at=datetime.now(timezone.utc),
            type=self.properties.art.to_parking_site_type(),
            purpose=PurposeType.BIKE,
        )
