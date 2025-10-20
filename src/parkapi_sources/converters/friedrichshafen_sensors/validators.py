"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.dataclasses import validataclass
from validataclass.validators import AnyOfValidator

from parkapi_sources.converters.base_converter.datex2 import UrbanParkingSite
from parkapi_sources.converters.base_converter.datex2.parking_record_status_validator import ParkingRecordStatus
from parkapi_sources.converters.base_converter.datex2.urban_parking_site_validator import Language
from parkapi_sources.models import (
    ParkingSpotRestrictionInput,
    RealtimeParkingSpotInput,
    StaticParkingSpotInput,
)
from parkapi_sources.models.enums import ParkingSiteType, ParkingSpotStatus, ParkingSpotType, PurposeType


@validataclass
class FriedrichshafenSensorsParkingSpot(UrbanParkingSite):
    # As Friedrichshafen uses a parking site model for parking spots, we have to ensure that the capacity is always 1
    parkingNumberOfSpaces: int = AnyOfValidator(allowed_values=['1'])

    def to_static_parking_spot_input(self) -> StaticParkingSpotInput:
        name_de: str | None = None
        for name in self.parkingName:
            if name.lang == Language.DE:
                name_de = name._text

        restrictions: list[ParkingSpotRestrictionInput] = []
        if self.assignedParkingAmongOthers:
            for user in self.assignedParkingAmongOthers.applicableForUser:
                restrictions.append(ParkingSpotRestrictionInput(type=user.to_parking_audience()))

        if self.urbanParkingSiteType.to_parking_site_type() == ParkingSiteType.ON_STREET:
            parking_spot_type = ParkingSpotType.ON_STREET
        elif self.parkingLayout.to_parking_site_type() is not None:
            parking_spot_type = ParkingSpotType[self.parkingLayout.to_parking_site_type().value]
        elif self.urbanParkingSiteType.to_parking_site_type() is not None:
            parking_spot_type = ParkingSpotType[self.urbanParkingSiteType.to_parking_site_type().value]
        else:
            parking_spot_type = None

        return StaticParkingSpotInput(
            uid=self.id,
            name=name_de,
            purpose=PurposeType.CAR,
            has_realtime_data=True,
            type=parking_spot_type,
            lat=self.parkingLocation.pointByCoordinates.pointCoordinates.latitude,
            lon=self.parkingLocation.pointByCoordinates.pointCoordinates.longitude,
            static_data_updated_at=self.parkingRecordVersionTime,
            restrictions=restrictions if len(restrictions) else None,
        )


@validataclass
class FriedrichshafenSensorsParkingRecordStatus(ParkingRecordStatus):
    def to_realtime_parking_spot_input(self) -> RealtimeParkingSpotInput:
        if self.parkingOccupancy.parkingNumberOfVacantSpaces:
            realtime_status = ParkingSpotStatus.AVAILABLE
        else:
            realtime_status = ParkingSpotStatus.TAKEN

        return RealtimeParkingSpotInput(
            uid=self.parkingRecordReference.id.split('[')[0],
            realtime_data_updated_at=self.parkingStatusOriginTime,
            realtime_status=realtime_status,
        )
