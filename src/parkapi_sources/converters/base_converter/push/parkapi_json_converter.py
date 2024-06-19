"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.push import JsonConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput


@validataclass
class ParkingSiteItemsInput:
    items: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))


class ParkApiConverter(JsonConverter, ABC):
    parking_site_items_validator = DataclassValidator(ParkingSiteItemsInput)
    static_parking_site_validator = DataclassValidator(StaticParkingSiteInput)
    realtime_parking_site_validator = DataclassValidator(RealtimeParkingSiteInput)

    def handle_json(
        self,
        data: dict | list,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        parking_site_inputs: list[StaticParkingSiteInput | RealtimeParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        try:
            parking_site_item_inputs = self.parking_site_items_validator.validate(data)
        except ValidationError as e:
            raise ImportSourceException(source_uid=self.source_info.uid, message=f'Invalid data {e.to_dict()}') from e

        for parking_site_dict in parking_site_item_inputs.items:
            try:
                static_parking_site_input = self.static_parking_site_validator.validate(parking_site_dict)
                parking_site_inputs.append(static_parking_site_input)
            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('uid'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )
                # If there was an error, we don't proceed with realtime data
                continue

            # No realtime data means no realtime data handling
            if not static_parking_site_input.has_realtime_data:
                continue

            try:
                parking_site_inputs.append(self.realtime_parking_site_validator.validate(parking_site_dict))
            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('uid'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return parking_site_inputs, parking_site_errors
