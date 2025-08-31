"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import abstractmethod

from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import KienzlerInput


class KienzlerBasePullConverter(ParkingSitePullConverter):
    kienzler_list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    kienzler_item_validator = DataclassValidator(KienzlerInput)

    @property
    @abstractmethod
    def config_prefix(self):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_config_keys = [
            f'PARK_API_KIENZLER_{self.config_prefix}_USER',
            f'PARK_API_KIENZLER_{self.config_prefix}_PASSWORD',
            f'PARK_API_KIENZLER_{self.config_prefix}_IDS',
        ]

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        kienzler_parking_sites, static_parking_site_errors = self._get_kienzler_parking_sites()

        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        for kienzler_parking_site in kienzler_parking_sites:
            static_parking_site_inputs.append(
                kienzler_parking_site.to_static_parking_site(self.source_info.public_url),
            )

        return self.apply_static_patches(static_parking_site_inputs), static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        kienzler_parking_sites, static_parking_site_errors = self._get_kienzler_parking_sites()
        for kienzler_parking_site in kienzler_parking_sites:
            realtime_parking_site_inputs.append(kienzler_parking_site.to_realtime_parking_site())

        return realtime_parking_site_inputs, static_parking_site_errors

    def _get_kienzler_parking_sites(self) -> tuple[list[KienzlerInput], list[ImportParkingSiteException]]:
        kienzler_item_inputs: list[KienzlerInput] = []
        errors: list[ImportParkingSiteException] = []

        parking_site_dicts = self.kienzler_list_validator.validate(self._request_kienzler())
        for parking_site_dict in parking_site_dicts:
            try:
                kienzler_item_inputs.append(self.kienzler_item_validator.validate(parking_site_dict))
            except ValidationError as e:
                errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('uid'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )
        return kienzler_item_inputs, errors

    def _request_kienzler(self) -> list[dict]:
        ids = self.config_helper.get(f'PARK_API_KIENZLER_{self.config_prefix}_IDS').split(',')
        result_dicts: list[dict] = []
        for i in range(0, len(ids), 25):
            response = self.request_post(
                url=f'{self.source_info.source_url}/index.php?eID=JSONAPI',
                json={
                    'user': self.config_helper.get(f'PARK_API_KIENZLER_{self.config_prefix}_USER'),
                    'password': self.config_helper.get(f'PARK_API_KIENZLER_{self.config_prefix}_PASSWORD'),
                    'action': 'capacity',
                    'context': 'unit',
                    'ids': self.config_helper.get(f'PARK_API_KIENZLER_{self.config_prefix}_IDS').split(',')[i : i + 25],
                },
                timeout=30,
            )
            result_dicts += response.json()

        return result_dicts


class KienzlerBikeAndRidePullConverter(KienzlerBasePullConverter):
    config_prefix = 'BIKE_AND_RIDE'

    source_info = SourceInfo(
        uid='kienzler_bike_and_ride',
        name='Kienzler: Bike and Ride',
        has_realtime_data=True,
        public_url='https://www.bikeandridebox.de',
        source_url='https://www.bikeandridebox.de',
    )


class KienzlerKarlsruhePullConverter(KienzlerBasePullConverter):
    config_prefix = 'KARLSRUHE'

    source_info = SourceInfo(
        uid='kienzler_karlruhe',
        name='Kienzler: Karlsruhe',
        has_realtime_data=True,
        public_url='https://www.bikeandridebox.de',
        source_url='https://www.bikeandridebox.de',
    )


class KienzlerNeckarsulmPullConverter(KienzlerBasePullConverter):
    config_prefix = 'NECKARSULM'

    source_info = SourceInfo(
        uid='kienzler_neckarsulm',
        name='Kienzler: Neckarsulm',
        has_realtime_data=True,
        public_url='https://www.bikeandridebox.de',
        source_url='https://www.bikeandridebox.de',
    )


class KienzlerOffenburgPullConverter(KienzlerBasePullConverter):
    config_prefix = 'OFFENBURG'

    source_info = SourceInfo(
        uid='kienzler_offenburg',
        name='Kienzler: Offenburg',
        has_realtime_data=True,
        public_url='https://www.fahrradparken-in-offenburg.de',
        source_url='https://www.fahrradparken-in-offenburg.de',
    )


class KienzlerRadSafePullConverter(KienzlerBasePullConverter):
    config_prefix = 'RADSAFE'

    source_info = SourceInfo(
        uid='kienzler_rad_safe',
        name='Kienzler: RadSafe',
        has_realtime_data=True,
        public_url='https://www.rad-safe.de',
        source_url='https://www.rad-safe.de',
    )


class KienzlerStuttgartPullConverter(KienzlerBasePullConverter):
    config_prefix = 'STUTTGART'

    source_info = SourceInfo(
        uid='kienzler_stuttgart',
        name='Kienzler: Stuttgart',
        has_realtime_data=True,
        public_url='https://stuttgart.bike-and-park.de',
        source_url='https://stuttgart.bike-and-park.de',
    )


class KienzlerVrnPullConverter(KienzlerBasePullConverter):
    config_prefix = 'VRN'

    source_info = SourceInfo(
        uid='kienzler_vrn',
        name='Kienzler: VRN',
        has_realtime_data=True,
        public_url='https://www.vrnradbox.de',
        source_url='https://www.vrnradbox.de',
    )


class KienzlerVVSPullConverter(KienzlerBasePullConverter):
    config_prefix = 'VVS'

    source_info = SourceInfo(
        uid='kienzler_vvs',
        name='Kienzler: VVS',
        has_realtime_data=True,
        public_url='https://vvs.bike-and-park.de',
        source_url='https://vvs.bike-and-park.de',
    )


class KienzlerUlmPullConverter(KienzlerBasePullConverter):
    """
    For unknown reasons, Ulm needs another authentication method. It provides the same data format, though.
    """

    config_prefix = 'ULM'

    source_info = SourceInfo(
        uid='kienzler_ulm',
        name='Kienzler: Ulm',
        has_realtime_data=True,
        public_url='https://ulm.bike-and-park.de',
        source_url='https://ulm.bike-and-park.de',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_config_keys = [
            f'PARK_API_KIENZLER_{self.config_prefix}_USER',
            f'PARK_API_KIENZLER_{self.config_prefix}_PASSWORD',
        ]

    def _request_kienzler(self) -> list[dict]:
        response = self.request_get(
            url=f'{self.source_info.source_url}/api/v1/capacity/units/all',
            auth=(
                self.config_helper.get(f'PARK_API_KIENZLER_{self.config_prefix}_USER'),
                self.config_helper.get(f'PARK_API_KIENZLER_{self.config_prefix}_PASSWORD'),
            ),
            timeout=30,
        )
        return response.json()
