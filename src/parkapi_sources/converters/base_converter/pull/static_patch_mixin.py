"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from abc import ABC
from json import JSONDecodeError
from pathlib import Path

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.models import (
    StaticBaseParkingInput,
    StaticParkingSiteInput,
    StaticParkingSitePatchInput,
    StaticParkingSpotInput,
    StaticParkingSpotPatchInput,
    StaticPatchInput,
)


class StaticPatchMixin(ABC):
    static_patch_input_validator = DataclassValidator(StaticPatchInput)
    parking_site_patch_validator = DataclassValidator(StaticParkingSitePatchInput)
    parking_spot_patch_validator = DataclassValidator(StaticParkingSpotPatchInput)
    _static_parking_patch_validator: DataclassValidator | None = None
    _config_value_for_patch_dir: str | None = None
    _current_parking_inputs_for_patch: list[StaticBaseParkingInput] | None = None

    @property
    def static_parking_patch_validator(self) -> DataclassValidator | None:
        if self._static_parking_patch_validator:
            return self._static_parking_patch_validator

        if self._current_parking_inputs_for_patch and isinstance(
            self._current_parking_inputs_for_patch[0],
            StaticParkingSiteInput,
        ):
            return self.parking_site_patch_validator

        if self._current_parking_inputs_for_patch and isinstance(
            self._current_parking_inputs_for_patch[0],
            StaticParkingSpotInput,
        ):
            return self.parking_spot_patch_validator

        return None

    @property
    def config_value_for_patch_dir(self) -> str | None:
        if self._config_value_for_patch_dir:
            return self._config_value_for_patch_dir

        if self._current_parking_inputs_for_patch and isinstance(
            self._current_parking_inputs_for_patch[0],
            StaticParkingSiteInput,
        ):
            return 'PARK_API_PARKING_SITE_PATCH_DIR'

        if self._current_parking_inputs_for_patch and isinstance(
            self._current_parking_inputs_for_patch[0],
            StaticParkingSpotInput,
        ):
            return 'PARK_API_PARKING_SPOT_PATCH_DIR'

        return None

    def apply_static_patches(self, parking_inputs: list[StaticBaseParkingInput]) -> list[StaticBaseParkingInput]:
        if not self.config_helper.get(self.config_value_for_patch_dir):
            return parking_inputs

        if not self.static_parking_patch_validator:
            return parking_inputs

        try:
            json_file_path = Path(
                self.config_helper.get(self.config_value_for_patch_dir), f'{self.source_info.uid}.json'
            )
        except TypeError:
            return parking_inputs

        if not json_file_path.exists():
            return parking_inputs

        with json_file_path.open() as json_file:
            try:
                item_dicts = json.loads(json_file.read())
            except JSONDecodeError:
                return parking_inputs

        parking_inputs_by_uid: dict[str, StaticBaseParkingInput] = {
            parking_input.uid: parking_input for parking_input in parking_inputs
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
