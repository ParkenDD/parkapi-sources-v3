"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.push import JsonConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput
from parkapi_sources.models.enums import SupervisionType

from .validation import PforzheimInput


class PforzheimPushConverter(JsonConverter):
    pforzheim_validator = DataclassValidator(PforzheimInput)

    source_info = SourceInfo(
        uid='pforzheim',
        name='Stadt Pforzheim',
        public_url='https://www.pforzheim.de',
        has_realtime_data=False,
    )

    def handle_json(self, data: dict | list) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        for input_dict in data:
            try:
                input_data: PforzheimInput = self.pforzheim_validator.validate(input_dict)
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('Id'),
                        message=f'validation error for {input_dict}: {e.to_dict()}',
                    ),
                )
                continue

            parking_site_input = StaticParkingSiteInput(
                uid=input_data.Id,
                name=input_data.name,
                type=input_data.type.to_parking_site_type_input(),
                lat=input_data.lat,
                lon=input_data.lon,
                address=input_data.address,
                description=input_data.description,
                capacity=input_data.capacity,
                capacity_woman=input_data.quantitySpacesReservedForWomen,
                capacity_disabled=input_data.quantitySpacesReservedForMobilityImpededPerson,
                fee_description=input_data.feeInformation,
                supervision_type=SupervisionType.YES if 'ja' in input_data.securityInformation.lower() else False,
                opening_hours='24/7' if input_data.hasOpeningHours24h else None,
                static_data_updated_at=datetime.now(tz=timezone.utc),
            )
            static_parking_site_inputs.append(parking_site_input)

        return static_parking_site_inputs, static_parking_site_errors
