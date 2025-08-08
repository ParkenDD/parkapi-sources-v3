"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from math import cos, pi

from parkapi_sources.util import round_7d

EARTH_RADIUS = 6371000
DEFAULT_DISTANCE = 2


def generate_point(lat: Decimal, lon: Decimal, number: int, max_number: int) -> tuple[Decimal, Decimal]:
    """
    This function helps to generate reproducible points around a given point.

    number and max_number should start at 0
    """

    # If we have just two points, then it's better to move both points, having the actual location in the middle
    if max_number == 1:
        match number:
            case 0:
                return move_lat(lat, int(0.5 * DEFAULT_DISTANCE)), lon
            case 1:
                return move_lat(lat, int(-0.5 * DEFAULT_DISTANCE)), lon

    if number == 0:
        return lat, lon

    multiplier = number // 8 + 1
    match number % 8:
        case 1:
            return move_lat(lat, DEFAULT_DISTANCE * multiplier), lon
        case 2:
            return lat, move_lon(lat, lon, -1 * DEFAULT_DISTANCE * multiplier)
        case 3:
            return move_lat(lat, -1 * DEFAULT_DISTANCE * multiplier), lon
        case 4:
            return lat, move_lon(lat, lon, DEFAULT_DISTANCE * multiplier)
        case 5:
            return move_lat(lat, DEFAULT_DISTANCE * multiplier), move_lon(lat, lon, -1 * DEFAULT_DISTANCE * multiplier)
        case 6:
            return move_lat(lat, -1 * DEFAULT_DISTANCE * multiplier), move_lon(
                lat, lon, -1 * DEFAULT_DISTANCE * multiplier
            )
        case 7:
            return move_lat(lat, -1 * DEFAULT_DISTANCE * multiplier), move_lon(lat, lon, DEFAULT_DISTANCE * multiplier)
        case 0:
            return move_lat(lat, DEFAULT_DISTANCE * multiplier), move_lon(lat, lon, DEFAULT_DISTANCE * multiplier)

    raise Exception('Match covers all possible values, which makes this statement impossible to reach.')


def move_lat(lat: Decimal, distance: int) -> Decimal:
    return round_7d(float(lat) + (distance / EARTH_RADIUS) * (180 / pi))


def move_lon(lat: Decimal, lon: Decimal, distance: int) -> Decimal:
    return round_7d(float(lon) + (distance / EARTH_RADIUS) * (180 / pi) / cos(float(lat) * pi / 180))
