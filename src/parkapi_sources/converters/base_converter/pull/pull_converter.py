"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import BaseConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportParkingSpotException
from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    RealtimeParkingSpotInput,
    StaticParkingSiteInput,
    StaticParkingSitePatchInput,
    StaticParkingSpotInput,
    StaticParkingSpotPatchInput,
)


class PullConverter(BaseConverter, ABC):
    pass


class ParkingSitePullConverter(PullConverter):
    config_value_for_patch_dir = 'PARK_API_PARKING_SITE_PATCH_DIR'
    static_parking_patch_validator = DataclassValidator(StaticParkingSitePatchInput)

    @abstractmethod
    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]: ...

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []

    def apply_static_patches(self, parking_inputs: list[StaticParkingSiteInput]) -> list[StaticParkingSiteInput]:
        return super().apply_static_patches(parking_inputs)  # type: ignore


class ParkingSpotPullConverter(PullConverter):
    static_parking_patch_validator = DataclassValidator(StaticParkingSpotPatchInput)
    config_value_for_patch_dir = 'PARK_API_PARKING_SPOT_PATCH_DIR'

    @abstractmethod
    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]: ...

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        return [], []

    def apply_static_patches(self, parking_inputs: list[StaticParkingSpotInput]) -> list[StaticParkingSpotInput]:
        return super().apply_static_patches(parking_inputs)  # type: ignore
