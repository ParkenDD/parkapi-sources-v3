"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import time
from typing import Optional

from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.validators import IntegerValidator, StringValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.validators import (
    ExcelNoneable,
    ExcelTimeValidator,
    GermanDurationIntegerValidator,
    MappedBooleanValidator,
    NumberCastingStringValidator,
)


class ExcelMappedBooleanValidator(MappedBooleanValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, mapping={'ja': True, 'nein': False}, **kwargs)


@validataclass
class ExcelStaticParkingSiteInput(StaticParkingSiteInput):
    operator_name: Optional[str] = ExcelNoneable(StringValidator(max_length=256))
    uid: str = NumberCastingStringValidator(min_length=1, max_length=256)
    has_lighting: Optional[bool] = ExcelNoneable(ExcelMappedBooleanValidator())
    has_fee: Optional[bool] = ExcelNoneable(ExcelMappedBooleanValidator())
    has_realtime_data: Optional[bool] = ExcelNoneable(ExcelMappedBooleanValidator(), default=False)
    max_stay: Optional[int] = ExcelNoneable(GermanDurationIntegerValidator()), Default(None)

    capacity: int = IntegerValidator(min_value=0)
    capacity_disabled: Optional[int] = ExcelNoneable(IntegerValidator(min_value=0))
    capacity_woman: Optional[int] = ExcelNoneable(IntegerValidator(min_value=0))
    capacity_family: Optional[int] = ExcelNoneable(IntegerValidator(min_value=0))
    capacity_charging: Optional[int] = ExcelNoneable(IntegerValidator(min_value=0))
    capacity_carsharing: Optional[int] = ExcelNoneable(IntegerValidator(min_value=0))
    capacity_truck: Optional[int] = ExcelNoneable(IntegerValidator(min_value=0))
    capacity_bus: Optional[int] = ExcelNoneable(IntegerValidator(min_value=0))


@validataclass
class ExcelOpeningTimeInput(ValidataclassMixin):
    opening_hours_is_24_7: Optional[bool] = ExcelNoneable(ExcelMappedBooleanValidator()), Default(None)
    opening_hours_weekday_begin: Optional[time] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_weekday_end: Optional[time] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_saturday_begin: Optional[time] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_saturday_end: Optional[time] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_sunday_begin: Optional[time] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_sunday_end: Optional[time] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_public_holiday_begin: Optional[time] = ExcelNoneable(ExcelTimeValidator()), Default(None)
    opening_hours_public_holiday_end: Optional[time] = ExcelNoneable(ExcelTimeValidator()), Default(None)

    def get_osm_opening_hours(self) -> str:
        if self.opening_hours_is_24_7 is True:
            return '24/7'
        # TODO: opening hours over midnight
        opening_hours_fragments = []
        if self.opening_hours_weekday_begin and self.opening_hours_weekday_end:
            opening_hours_fragments.append(
                f'Mo-Fr {self.opening_hours_weekday_begin.strftime("%H:%M")}-{self.opening_hours_weekday_end.strftime("%H:%M")}',
            )
        if self.opening_hours_saturday_begin and self.opening_hours_saturday_end:
            opening_hours_fragments.append(
                f'Sa {self.opening_hours_saturday_begin.strftime("%H:%M")}-{self.opening_hours_saturday_end.strftime("%H:%M")}',
            )
        if self.opening_hours_sunday_begin and self.opening_hours_sunday_end:
            opening_hours_fragments.append(
                f'Su {self.opening_hours_sunday_begin.strftime("%H:%M")}-{self.opening_hours_sunday_end.strftime("%H:%M")}',
            )
        if self.opening_hours_public_holiday_begin and self.opening_hours_public_holiday_end:
            opening_hours_fragments.append(
                f'PH {self.opening_hours_public_holiday_begin.strftime("%H:%M")}-{self.opening_hours_public_holiday_end.strftime("%H:%M")}',
            )
        return '; '.join(opening_hours_fragments)
