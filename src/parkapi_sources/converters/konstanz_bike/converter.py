"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import override

from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import KonstanzBikeParkingSiteInput


class KonstanzBikePullConverter(ParkingSitePullConverter):
    list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    konstanz_bike_validator = DataclassValidator(KonstanzBikeParkingSiteInput)

    source_info = SourceInfo(
        uid='konstanz_bike',
        name='Stadt Konstanz: Fahrrad-Abstellanlagen',
        public_url='https://www.konstanz.de/',
        source_url='https://services-eu1.arcgis.com/cgMeYTGtzFtnxdsx/arcgis/rest/services/Fahrradverkehr/FeatureServer/7/query?outFields=*&where=1%3D1&f=geojson',
        timezone='Europe/Berlin',
        has_realtime_data=False,
    )

    @override
    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        konstanz_parking_site_inputs, static_parking_site_errors = self._get_parking_site_inputs()

        static_parking_sites: list[StaticParkingSiteInput] = []
        for parking_site_input in konstanz_parking_site_inputs:
            static_parking_sites.append(parking_site_input.to_static_parking_site_input())

        return self.apply_static_patches(static_parking_sites), static_parking_site_errors

    @override
    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []  # Only static data can be called from the API

    def _get_parking_site_inputs(self) -> tuple[list[KonstanzBikeParkingSiteInput], list[ImportParkingSiteException]]:
        konstanz_bike_parking_sites: list[KonstanzBikeParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        response = self.request_get(url=self.source_info.source_url, timeout=60)
        parking_site_inputs = response.json()['features']

        for parking_site in parking_site_inputs:
            try:
                konstanz_bike_parking_sites.append(self.konstanz_bike_validator.validate(parking_site))
            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site.get('id'),
                        message=f'validation error for static data {parking_site}: {e.to_dict()}',
                    ),
                )

        return konstanz_bike_parking_sites, parking_site_errors
