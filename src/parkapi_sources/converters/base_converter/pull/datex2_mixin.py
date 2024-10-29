"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

import pyproj
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput


class Datex2Mixin(ABC):
    proj: pyproj.Proj | None = None
    static_parking_site_validator: DataclassValidator

    @property
    @abstractmethod
    def source_info(self) -> SourceInfo:
        pass

    def _handle_datex2_parking_facilities(
        self, datex2_parking_facilities: dict
    ) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []
        static_items = (
            datex2_parking_facilities.get('parkingFacilityTablePublication', {})
            .get('parkingFacilityTable', {})
            .get('parkingFacility', [])
        )

        for static_item in static_items:
            try:
                static_parking_site_inputs.append(self._handle_datex2_parking_facility(static_item))
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=static_item.get('id'),
                        message=str(e.to_dict()),
                    )
                )

        return static_parking_site_inputs, static_parking_site_errors

    def _handle_datex2_parking_facility(self, datex2_parking_facility: dict) -> StaticParkingSiteInput:
        input_data = {
            'uid': datex2_parking_facility.get('id'),
            'name': datex2_parking_facility.get('parkingFacilityName'),
            'has_realtime_data': True,
            'capacity': int(datex2_parking_facility.get('totalParkingCapacity')),
            'static_data_updated_at': datex2_parking_facility.get('parkingFacilityRecordVersionTime'),
        }

        # Coordinates
        coordinates_base = datex2_parking_facility.get('facilityLocation', {}).get('locationForDisplay', {})
        if self.proj is None:
            input_data['lat'] = coordinates_base.get('latitude')
            input_data['lon'] = coordinates_base.get('longitude')
        else:
            coordinates = self.proj(
                float(coordinates_base.get('longitude')),
                float(coordinates_base.get('latitude')),
                inverse=True,
            )
            input_data['lat'] = coordinates[1]
            input_data['lon'] = coordinates[0]

        # max_height
        height_base = datex2_parking_facility.get('characteristicsOfPermittedVehicles', {}).get(
            'heightCharacteristic', {}
        )
        if height_base.get('comparisonOperator') == 'lessThan' and height_base.get('vehicleHeight'):
            input_data['max_height'] = int(float(height_base.get('vehicleHeight')) * 1000)

        # Sub-Capacities
        mapping: list[tuple[tuple[str, str], str]] = [
            (('personTypeForWhichSpacesAssigned', 'disabled'), 'capacity_disabled'),
            (('personTypeForWhichSpacesAssigned', 'families'), 'capacity_family'),
            (('personTypeForWhichSpacesAssigned', 'women'), 'capacity_woman'),
            (('characteristicsOfVehiclesForWhichSpacesAssigned', {'fuelType': 'battery'}), 'capacity_charging'),
        ]

        for sub_capacity in datex2_parking_facility.get('assignedParkingSpaces', []):
            assigned_parking_spaces = sub_capacity.get('assignedParkingSpaces', {}).get(
                'descriptionOfAssignedParkingSpaces', {}
            )
            for key, value in assigned_parking_spaces.items():
                for map_key_components, final_key in mapping:
                    if map_key_components[0] == key and map_key_components[1] == value:
                        input_data[final_key] = int(
                            sub_capacity.get('assignedParkingSpaces')['numberOfAssignedParkingSpaces'],
                        )
                        break

        # TODO: parse opening times with more information, for now they are broken

        return self.static_parking_site_validator.validate(input_data)
