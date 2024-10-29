"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import time

import pytest

from parkapi_sources.models import ExcelOpeningTimeInput


@pytest.mark.parametrize(
    'input_data,output_data',
    [
        (
            {'opening_hours_is_24_7': True},
            '24/7',
        ),
        (
            {
                'opening_hours_weekday_begin': time(10),
                'opening_hours_weekday_end': time(20),
            },
            'Mo-Fr 10:00-20:00',
        ),
        (
            {
                'opening_hours_weekday_begin': time(10, 30),
                'opening_hours_weekday_end': time(20, 30),
            },
            'Mo-Fr 10:30-20:30',
        ),
        (
            {
                'opening_hours_saturday_begin': time(10),
                'opening_hours_saturday_end': time(20),
            },
            'Sa 10:00-20:00',
        ),
        (
            {
                'opening_hours_sunday_begin': time(10),
                'opening_hours_sunday_end': time(20),
            },
            'Su 10:00-20:00',
        ),
        (
            {
                'opening_hours_public_holiday_begin': time(10),
                'opening_hours_public_holiday_end': time(20),
            },
            'PH 10:00-20:00',
        ),
        (
            {
                'opening_hours_weekday_begin': time(8),
                'opening_hours_weekday_end': time(20),
                'opening_hours_saturday_begin': time(10),
                'opening_hours_saturday_end': time(18),
                'opening_hours_sunday_begin': time(12),
                'opening_hours_sunday_end': time(15),
                'opening_hours_public_holiday_begin': time(11),
                'opening_hours_public_holiday_end': time(12),
            },
            'Mo-Fr 08:00-20:00; Sa 10:00-18:00; Su 12:00-15:00; PH 11:00-12:00',
        ),
    ],
)
def test_xlsx_opening_times_to_osm(input_data: dict, output_data: str):
    opening_time_input = ExcelOpeningTimeInput(**input_data)
    assert opening_time_input.get_osm_opening_hours() == output_data
