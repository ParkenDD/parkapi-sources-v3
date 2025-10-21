"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from abc import ABC, abstractmethod
from json import JSONDecodeError
from pathlib import Path

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import BaseConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportParkingSpotException
from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    RealtimeParkingSpotInput,
    StaticBaseParkingInput,
    StaticParkingSiteInput,
    StaticParkingSitePatchInput,
    StaticParkingSpotInput,
    StaticParkingSpotPatchInput,
    StaticPatchInput,
)


class PullConverter(BaseConverter, ABC):
    static_patch_input_validator = DataclassValidator(StaticPatchInput)

    @property
    @abstractmethod
    def static_parking_patch_validator(self): ...

    @property
    @abstractmethod
    def config_value_for_patch_dir(self) -> str: ...

    def apply_static_patches(self, parking_inputs: list[StaticBaseParkingInput]) -> list[StaticBaseParkingInput]:
        if not self.config_helper.get(self.config_value_for_patch_dir):
            return parking_inputs

        json_file_path = Path(self.config_helper.get(self.config_value_for_patch_dir), f'{self.source_info.uid}.json')

        if not json_file_path.exists():
            return parking_inputs

        with json_file_path.open() as json_file:
            try:
                item_dicts = json.loads(json_file.read())
            except JSONDecodeError:
                return parking_inputs

        parking_inputs_by_uid: dict[str, StaticBaseParkingInput] = {
            parking_spot_input.uid: parking_spot_input for parking_spot_input in parking_inputs
        }

        try:
            items = self.static_patch_input_validator.validate(item_dicts)
        except ValidationError:
            return parking_inputs

        for item_dict in items.items:
            try:
                parking_patch = self.static_parking_patch_validator.validate(item_dict)
            except ValidationError:
                continue

            if parking_patch.uid not in parking_inputs_by_uid:
                continue

            for key, value in parking_patch.to_dict().items():
                if key in ['external_identifiers', 'restrictions']:
                    continue
                setattr(parking_inputs_by_uid[parking_patch.uid], key, value)
            if parking_patch.external_identifiers:
                parking_inputs_by_uid[parking_patch.uid].external_identifiers = parking_patch.external_identifiers
            if parking_patch.restrictions:
                parking_inputs_by_uid[parking_patch.uid].restrictions = parking_patch.restrictions

        return parking_inputs


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
