"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime, time, timezone
from decimal import Decimal
from enum import Enum

from validataclass.dataclasses import validataclass
from validataclass.validators import DateValidator, EnumValidator, IntegerValidator, NumericValidator, StringValidator

from parkapi_sources.models import (
    ParkAndRideType,
    ParkingAudience,
    ParkingSiteRestrictionInput,
    ParkingSiteType,
    StaticParkingSiteInput,
)
from parkapi_sources.models.xlsx_inputs import ExcelMappedBooleanValidator
from parkapi_sources.validators import NumberCastingStringValidator


class KelternParkingSiteType(Enum):
    ON_STREET = 'onStreet'
    CAR_PARK = 'carPark'
    PARK_AND_RIDE = 'parkAndRide'
    DISABLED = 'handicapped'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.ON_STREET: ParkingSiteType.ON_STREET,
            self.CAR_PARK: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.PARK_AND_RIDE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.DISABLED: ParkingSiteType.ON_STREET,
        }.get(self)


@validataclass
class KelternRowInput:
    id: str = StringValidator()
    name: str = StringValidator()
    locations_longitude: Decimal = NumericValidator()
    locations_latitude: Decimal = NumericValidator()
    operatorID: str = StringValidator()
    timestamp: date = DateValidator()
    adress_str: str = StringValidator()
    adress_pos: str = NumberCastingStringValidator()
    adress_cit: str = StringValidator()
    descriptio: str = StringValidator()
    type: KelternParkingSiteType = EnumValidator(KelternParkingSiteType)
    quantitySpacesReservedForWomen: int = IntegerValidator()
    quantitySpacesReservedForMobilityImpededPerson: int = IntegerValidator()
    capacity: int = IntegerValidator()
    hasChargingStation: bool = ExcelMappedBooleanValidator()
    hasOpeningHours24h: bool = ExcelMappedBooleanValidator()
    openingHours: str = StringValidator()

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        description_fragments: list[str] = []
        opening_hours_description = self.openingHours.replace('24h, 7 Tage', '').strip()
        if opening_hours_description:
            description_fragments.append(opening_hours_description)
        description = self.descriptio.strip()
        if description and description != '-':
            description_fragments.append(self.descriptio.strip())

        static_parking_site = StaticParkingSiteInput(
            uid=self.id.replace('@GemeindeKeltern', ''),
            capacity=self.capacity,
            name=self.adress_str,
            opening_hours='24/7' if self.hasOpeningHours24h else None,
            description='; '.join(description_fragments),
            address=f'{self.adress_str}, {self.adress_pos} {self.adress_cit}',
            static_data_updated_at=datetime.combine(self.timestamp, time(12), tzinfo=timezone.utc),
            park_and_ride_type=[ParkAndRideType.YES] if self.type == KelternParkingSiteType.PARK_AND_RIDE else None,
            type=self.type.to_parking_site_type(),
            has_realtime_data=False,
            lat=self.locations_latitude,
            lon=self.locations_longitude,
        )
        if self.type == KelternParkingSiteType.DISABLED or self.hasChargingStation:
            static_parking_site.restrictions = []
        if self.type == KelternParkingSiteType.DISABLED:
            static_parking_site.restrictions = [
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.DISABLED,
                ),
            ]
        if self.hasChargingStation:
            static_parking_site.restrictions = [
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                    capacity=1,
                ),
            ]
        return static_parking_site
