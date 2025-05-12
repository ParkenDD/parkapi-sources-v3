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
    StaticParkingSiteInput,
    StaticParkingSitePatchInput,
    StaticParkingSpotInput,
    StaticPatchInput,
)


class PullConverter(BaseConverter, ABC): ...


class ParkingSitePullConverter(PullConverter):
    static_patch_input_validator = DataclassValidator(StaticPatchInput)
    static_parking_site_patch_validator = DataclassValidator(StaticParkingSitePatchInput)

    @abstractmethod
    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]: ...

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []

    def apply_static_patches(self, parking_site_inputs: list[StaticParkingSiteInput]) -> list[StaticParkingSiteInput]:
        if not self.config_helper.get('PARK_API_PARKING_SITE_PATCH_DIR'):
            return parking_site_inputs

        json_file_path = Path(self.config_helper.get('PARK_API_PARKING_SITE_PATCH_DIR'), f'{self.source_info.uid}.json')

        if not json_file_path.exists():
            return parking_site_inputs

        with json_file_path.open() as json_file:
            try:
                item_dicts = json.loads(json_file.read())
            except JSONDecodeError:
                return parking_site_inputs

        parking_site_inputs_by_uid: dict[str, StaticParkingSiteInput] = {
            parking_site_input.uid: parking_site_input for parking_site_input in parking_site_inputs
        }

        try:
            items = self.static_patch_input_validator.validate(item_dicts)
        except ValidationError:
            return parking_site_inputs

        for item_dict in items.items:
            try:
                parking_site_patch = self.static_parking_site_patch_validator.validate(item_dict)
            except ValidationError:
                continue

            if parking_site_patch.uid not in parking_site_inputs_by_uid:
                continue

            for key, value in parking_site_patch.to_dict().items():
                setattr(parking_site_inputs_by_uid[parking_site_patch.uid], key, value)

        return parking_site_inputs


class ParkingSpotPullConverter(PullConverter):
    @abstractmethod
    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]: ...

    def get_realtime_parking_spots(self) -> tuple[list[RealtimeParkingSpotInput], list[ImportParkingSpotException]]:
        return [], []
