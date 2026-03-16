"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from abc import ABC, abstractmethod
from json import JSONDecodeError
from pathlib import Path
from typing import Unpack

from requests import Response
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    RealtimeParkingSpotInput,
    SourceInfo,
    StaticBaseParkingInput,
    StaticParkingSiteInput,
    StaticParkingSitePatchInput,
    StaticParkingSpotInput,
    StaticParkingSpotPatchInput,
    StaticPatchInput,
)
from parkapi_sources.util import ConfigHelper, RequestHelper
from parkapi_sources.util.request_helper import RequestKwargs


class BaseConverter(ABC):
    config_helper: ConfigHelper
    request_helper: RequestHelper
    static_parking_site_validator = DataclassValidator(StaticParkingSiteInput)
    realtime_parking_site_validator = DataclassValidator(RealtimeParkingSiteInput)
    static_parking_spot_validator = DataclassValidator(StaticParkingSpotInput)
    realtime_parking_spot_validator = DataclassValidator(RealtimeParkingSpotInput)
    static_patch_input_validator = DataclassValidator(StaticPatchInput)
    required_config_keys: list[str] = []

    def __init__(self, config_helper: ConfigHelper, request_helper: RequestHelper):
        self.config_helper = config_helper
        self.request_helper = request_helper

    @property
    @abstractmethod
    def source_info(self) -> SourceInfo:
        pass

    @property
    @abstractmethod
    def static_parking_patch_validator(self) -> DataclassValidator:
        pass

    @property
    @abstractmethod
    def config_value_for_patch_dir(self) -> str:
        pass

    def request_get(self, **kwargs: Unpack[RequestKwargs]) -> Response:
        return self.request_helper.get(source_info=self.source_info, **kwargs)

    def request_post(self, **kwargs: Unpack[RequestKwargs]) -> Response:
        return self.request_helper.post(source_info=self.source_info, **kwargs)

    def request_put(self, **kwargs: Unpack[RequestKwargs]) -> Response:
        return self.request_helper.put(source_info=self.source_info, **kwargs)

    def request_patch(self, **kwargs: Unpack[RequestKwargs]) -> Response:
        return self.request_helper.patch(source_info=self.source_info, **kwargs)

    def request_delete(self, **kwargs: Unpack[RequestKwargs]) -> Response:
        return self.request_helper.delete(source_info=self.source_info, **kwargs)

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


class ParkingSiteBaseConverter(BaseConverter, ABC):
    static_parking_patch_validator = DataclassValidator(StaticParkingSitePatchInput)
    config_value_for_patch_dir = 'PARK_API_PARKING_SITE_PATCH_DIR'


class ParkingSpotBaseConverter(BaseConverter, ABC):
    static_parking_patch_validator = DataclassValidator(StaticParkingSpotPatchInput)
    config_value_for_patch_dir = 'PARK_API_PARKING_SPOT_PATCH_DIR'
