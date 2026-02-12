"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime, time, timezone
from enum import Enum, StrEnum, auto
from typing import Any

from typing_extensions import override
from validataclass.dataclasses import DefaultUnset, ValidataclassMixin, validataclass
from validataclass.helpers import OptionalUnset
from validataclass.validators import (
    DataclassValidator,
    DateValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    NoneToUnsetValue,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import GeojsonBaseFeatureInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType, SupervisionType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import MappedBooleanValidator, ParsedDateValidator


class HerrenbergBikeType(StrEnum):
    BÜGEL = auto()
    REINE_VORDERRADHALTERUNG = auto()
    BÜGEL_PLUS_VORDERRADHALTERUNG = auto()
    SCHLIEẞFÄCHER_BOXEN = auto()
    ANDERE = auto()

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


@validataclass
class HerrenbergBikePropertiesInput(ValidataclassMixin):
    fid: int = IntegerValidator(min_value=1)  # to uid
    Standortbeschreibung: str = StringValidator(multiline=True)  # to name
    Erfassungsdatum: date = DateValidator()  # static_data_updated_at, no conversion
    Typ_Anlage: HerrenbergBikeType = EnumValidator(HerrenbergBikeType)  # mapped to type
    Davon_Ueberdacht: int = IntegerValidator()  # >=1 True else False
    Anzahl_E_Ladepunkte: int = IntegerValidator()  # restrictions (type: CHARGING capacity: str to int)
    Gebuehrenpflichtig: bool = MappedBooleanValidator(mapping={'ja': True, 'nein': False})
    SonstigeAnmrkungen: str = StringValidator(multiline=True)  # optional, should be unset if ""
    OSM_ID: str = StringValidator()  # -> external_identifiers (type:OSM value: ## )

    @override
    def to_dict(self, *, keep_unset_values: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {}

        result['uid'] = self.fid
        result['name'] = self.StandortBeschreibung
        result['static_data_updated_at'] = self.Erfassungdatum
        result['type'] = HerrenbergBikeType(self.Typ_Anlage).to_parking_site_type()
        result['is_covered'] = self.Davon_Ueberdacht > 0
        result['restriction']
        result['has_fee']
        result['has_lighting']
        if description := self.SonstigeAnmerkungen:
            result['description'] = descripion
        else:
            result['description'] = None

        result['external_identifier'] = {'type': 'OSM', 'value': self.OSM_ID}

        return result


@validataclass
class HerrenbergBikeFeatureInput(GeojsonBaseFeatureInput):
    properties: DataclassValidator[HerrenbergBikePropertiesInput] = DataclassValidator(HerrenbergBikePropertiesInput)

    @override
    def to_static_parking_site_input(self, **kwargs: Any) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            has_realtime_data=False,
            **self.properties.to_dict(**kwargs),
        )
