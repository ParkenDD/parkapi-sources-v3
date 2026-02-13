"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any

from typing_extensions import NotRequired, TypedDict, override
from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.validators import (
    DataclassValidator,
    DateValidator,
    EnumValidator,
    IntegerValidator,
    StringValidator,
)

from parkapi_sources.models import GeojsonBaseFeatureInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ExternalIdentifierType, ParkingAudience, ParkingSiteType
from parkapi_sources.models.parking_site_inputs import ParkingSiteRestrictionInput
from parkapi_sources.models.shared_inputs import ExternalIdentifierInput
from parkapi_sources.util import round_7d
from parkapi_sources.util.dict import AnyDict
from parkapi_sources.validators import MappedBooleanValidator


class HerrenbergBikeType(StrEnum):
    BÜGEL = 'Bügel'
    REINE_VORDERRADHALTERUNG = 'Reine Vorderradhalterung'
    BÜGEL_PLUS_VORDERRADHALTERUNG = 'Bügel + Vorderradhalterung'
    SCHLIEẞFÄCHER_BOXEN = 'Schließfächer/ Boxen'
    ANDERE = 'andere'

    def to_parking_site_type(self) -> ParkingSiteType:
        match self:
            case self.SCHLIEẞFÄCHER_BOXEN:
                return ParkingSiteType.LOCKBOX
            case self.BÜGEL:
                return ParkingSiteType.STANDS
            case self.REINE_VORDERRADHALTERUNG:
                return ParkingSiteType.WALL_LOOPS
            case self.BÜGEL_PLUS_VORDERRADHALTERUNG:
                return ParkingSiteType.SAFE_WALL_LOOPS
            case self.ANDERE:
                return ParkingSiteType.FLOOR


class HerrenbergProperties(TypedDict):
    uid: str
    name: str
    static_data_updated_at: datetime
    type: ParkingSiteType
    capacity: int
    description: str | None
    is_covered: NotRequired[bool]
    has_fee: NotRequired[int]
    has_lighting: NotRequired[int]
    external_identifiers: NotRequired[list[ExternalIdentifierInput]]
    restrictions: NotRequired[list[ParkingSiteRestrictionInput]]


@validataclass
class HerrenbergBikePropertiesInput(ValidataclassMixin):
    fid: int = IntegerValidator(min_value=1)
    Standortbeschreibung: str = StringValidator(multiline=True)
    Erfassungsdatum: date = DateValidator()
    Typ_Anlage: HerrenbergBikeType = EnumValidator(HerrenbergBikeType)
    Anzahl_Abstellmoeglichkeiten: int = IntegerValidator()
    Davon_Ueberdacht: int | None = IntegerValidator(), Default(None)
    Anzahl_E_Ladepunkte: int | None = IntegerValidator(allow_strings=True), Default(None)
    Gebuehrenpflichtig: bool | None = MappedBooleanValidator(mapping={'ja': True, 'nein': False}), Default(None)
    Beleuchtet: bool | None = MappedBooleanValidator(mapping={'ja': True, 'nein': False, '': False}), Default(None)
    SonstigeAnmrkungen: str = StringValidator(multiline=True), Default(None)
    OSM_ID: str | None = StringValidator(), Default(None)

    @override
    def to_dict(self, *, keep_unset_values: bool = False) -> AnyDict:
        result: HerrenbergProperties = {
            'uid': str(self.fid),
            'name': self.remove_new_lines(self.Standortbeschreibung),
            'static_data_updated_at': datetime.combine(self.Erfassungsdatum, datetime.min.time(), timezone.utc),
            'type': HerrenbergBikeType(self.Typ_Anlage).to_parking_site_type(),
            'description': self.SonstigeAnmrkungen,
            'capacity': self.Anzahl_Abstellmoeglichkeiten,
        }

        if self.Davon_Ueberdacht:
            result['is_covered'] = self.Davon_Ueberdacht > 0

        if self.Gebuehrenpflichtig:
            result['has_fee'] = self.Gebuehrenpflichtig

        if self.Beleuchtet:
            result['has_lighting'] = self.Beleuchtet

        if self.OSM_ID:
            result['external_identifiers'] = [
                ExternalIdentifierInput(type=ExternalIdentifierType.OSM, value=self.OSM_ID)
            ]

        result['restrictions'] = self.get_restrictions(self.Anzahl_E_Ladepunkte)

        return dict(result)

    @staticmethod
    def get_restrictions(capacity: int | None) -> list[ParkingSiteRestrictionInput]:
        restriction = ParkingSiteRestrictionInput()

        if capacity:
            restriction = ParkingSiteRestrictionInput(capacity=capacity, type=ParkingAudience.CHARGING)

        return [restriction]

    @staticmethod
    def remove_new_lines(input: str) -> str:
        return input.replace('\n', '; ')


@validataclass
class HerrenbergBikeFeatureInput(GeojsonBaseFeatureInput):
    properties: DataclassValidator[HerrenbergBikePropertiesInput] = DataclassValidator(HerrenbergBikePropertiesInput)

    @override
    def to_static_parking_site_input(self, **kwargs: Any) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            has_realtime_data=False,
            **self.properties.to_dict(),
        )
