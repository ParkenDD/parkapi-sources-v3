"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum


class PurposeType(Enum):
    CAR = 'CAR'
    BIKE = 'BIKE'
    MOTORCYCLE = 'MOTORCYCLE'
    ITEM = 'ITEM'


class SourceStatus(Enum):
    DISABLED = 'DISABLED'
    ACTIVE = 'ACTIVE'
    FAILED = 'FAILED'
    PROVISIONED = 'PROVISIONED'


class ParkingSiteType(Enum):
    # For cars
    ON_STREET = 'ON_STREET'
    OFF_STREET_PARKING_GROUND = 'OFF_STREET_PARKING_GROUND'
    UNDERGROUND = 'UNDERGROUND'
    CAR_PARK = 'CAR_PARK'

    # For bikes. See https://wiki.openstreetmap.org/wiki/Key:bicycle_parking for explanations.
    WALL_LOOPS = 'WALL_LOOPS'
    SAFE_WALL_LOOPS = 'SAFE_WALL_LOOPS'
    STANDS = 'STANDS'
    LOCKERS = 'LOCKERS'
    SHED = 'SHED'
    TWO_TIER = 'TWO_TIER'
    BUILDING = 'BUILDING'
    FLOOR = 'FLOOR'

    # For separate lockers
    LOCKBOX = 'LOCKBOX'

    # For all
    OTHER = 'OTHER'


class ParkingSpotType(Enum):
    # For cars
    ON_STREET = 'ON_STREET'
    OFF_STREET_PARKING_GROUND = 'OFF_STREET_PARKING_GROUND'
    UNDERGROUND = 'UNDERGROUND'
    CAR_PARK = 'CAR_PARK'

    # For bikes. See https://wiki.openstreetmap.org/wiki/Key:bicycle_parking for explanations.
    LOCKERS = 'LOCKERS'

    # For separate lockers
    LOCKBOX = 'LOCKBOX'


class ParkAndRideType(Enum):
    CARPOOL = 'CARPOOL'
    TRAIN = 'TRAIN'
    BUS = 'BUS'
    TRAM = 'TRAM'
    YES = 'YES'
    NO = 'NO'


class OpeningStatus(Enum):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    UNKNOWN = 'UNKNOWN'


class ExternalIdentifierType(Enum):
    OSM = 'OSM'
    DHID = 'DHID'


class SupervisionType(Enum):
    YES = 'YES'
    NO = 'NO'
    VIDEO = 'VIDEO'
    ATTENDED = 'ATTENDED'


class ParkingSpotStatus(Enum):
    AVAILABLE = 'AVAILABLE'
    TAKEN = 'TAKEN'
    UNKNOWN = 'UNKNOWN'


class ParkingAudience(Enum):
    DISABLED = 'DISABLED'
    WOMEN = 'WOMEN'
    FAMILY = 'FAMILY'
    CARSHARING = 'CARSHARING'
    CHARGING = 'CHARGING'
    TAXI = 'TAXI'
    PRIVATE = 'PRIVATE'
    DELIVERY = 'DELIVERY'
    TRUCK = 'TRUCK'
    BUS = 'BUS'
    NO_PARKING = 'NO_PARKING'
    NO_STOPPING = 'NO_STOPPING'
    CUSTOMER = 'CUSTOMER'
    RESIDENT = 'RESIDENT'
    CARAVAN = 'CARAVAN'


class ParkingSiteSide(Enum):
    RIGHT = 'RIGHT'
    LEFT = 'LEFT'


class ParkingSiteOrientation(Enum):
    PARALLEL = 'PARALLEL'
    DIAGONAL = 'DIAGONAL'
    PERPENDICULAR = 'PERPENDICULAR'


class ParkingType(Enum):
    LANE = 'LANE'
    ON_KERB = 'ON_KERB'
    HALF_ON_KERB = 'HALF_ON_KERB'
    SHOULDER = 'SHOULDER'
