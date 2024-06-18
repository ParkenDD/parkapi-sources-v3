"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from parkapi_sources.validators import ExcelNoneable
from parkapi_sources.validators.boolean_validators import MappedBooleanValidator


@validataclass
class PolygonListValidator(StringValidator):
    def validate(self, input_data: Any, **kwargs) -> list[tuple[Decimal, Decimal]]:
        input_data = super().validate(input_data, **kwargs)
        items = input_data.split(',')
        try:
            return [(Decimal(items[i]), Decimal(items[i + 1])) for i in range(0, len(items), 2)]
        except ValueError as e:
            raise ValidationError(code='invalid_polygon', reason='Invalid polygon data') from e


class KonstanzBikeParkingSiteType(Enum):
    STANDS_BOTH_SIDE = 'Anlehnbügel beidseitig'
    STANDS_SINGLE_SIDE = 'Anlehnbügel einseitig'
    EXTENDED_STANDS = 'Anlehnbügel mit Rahmenhalter'
    WALL_LOOPS = 'Vorderradhalter'
    SAFE_WALL_LOOPS = 'Vorderrad-Rahmenhalter'
    FLOOR = 'Markierte Fläche'
    LOCKERS = 'Fahrradbox'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        return {
            self.STANDS_BOTH_SIDE: ParkingSiteType.STANDS,
            self.STANDS_SINGLE_SIDE: ParkingSiteType.STANDS,
            self.EXTENDED_STANDS: ParkingSiteType.STANDS,
            self.WALL_LOOPS: ParkingSiteType.WALL_LOOPS,
            self.SAFE_WALL_LOOPS: ParkingSiteType.SAFE_WALL_LOOPS,
            self.FLOOR: ParkingSiteType.FLOOR,
            self.LOCKERS: ParkingSiteType.LOCKERS,
        }.get(self)


class KonstanzBikeGeometry(Enum):
    POLYGON = 'Polygon'
    MULTI_POLYGON = 'MultiPolygon'


@validataclass
class KonstanzRowInput:
    uid: int = IntegerValidator(allow_strings=True)
    operator_name: str = StringValidator()
    district: str = StringValidator()
    capacity: int = IntegerValidator(min_value=1, allow_strings=True)
    address: str = StringValidator(min_length=1)
    type: KonstanzBikeParkingSiteType = EnumValidator(KonstanzBikeParkingSiteType)
    has_lighting: Optional[bool] = ExcelNoneable(MappedBooleanValidator(mapping={'1': True, '0': False}))
    is_covered: Optional[bool] = ExcelNoneable(MappedBooleanValidator(mapping={'1': True, '0': False}))
    coordinates: list[tuple[Decimal, Decimal]] = PolygonListValidator()
    geometry: KonstanzBikeGeometry = EnumValidator(KonstanzBikeGeometry)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.uid),
            name=self.address,
            lat=sum([coordinate[1] for coordinate in self.coordinates]) / len(self.coordinates),
            lon=sum([coordinate[0] for coordinate in self.coordinates]) / len(self.coordinates),
            type=self.type.to_parking_site_type_input(),
            address=f'{self.address}, Konstanz',
            capacity=self.capacity,
            has_lighting=self.has_lighting,
            is_covered=self.is_covered,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            purpose=PurposeType.BIKE,
        )
