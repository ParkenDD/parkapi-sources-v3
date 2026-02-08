"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import GeojsonInput, RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import BonnFeatureInput


class BonnPullConverter(ParkingSitePullConverter):
    geojson_validator = DataclassValidator(GeojsonInput)
    bonn_feature_validator = DataclassValidator(BonnFeatureInput)

    source_info = SourceInfo(
        uid='bonn',
        name='Stadt Bonn',
        public_url='https://opendata.bonn.de/dataset/standorte-der-parkpl%C3%A4tze-pkw-motorrad-wohnmobilwohnwagen-und-busparkpl%C3%A4tze',
        source_url='https://stadtplan.bonn.de/geojson?Thema=21090',
        has_realtime_data=False,
        attribution_license='CC0-1.0',
        attribution_contributor='Stadt Bonn',
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        response = self.request_get(url=self.source_info.source_url, timeout=30)
        geojson_input = self.geojson_validator.validate(response.json())

        for feature_dict in geojson_input.features:
            try:
                bonn_feature = self.bonn_feature_validator.validate(feature_dict)
                static_parking_site_inputs.append(bonn_feature.to_static_parking_site())
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=feature_dict.get('properties', {}).get('parkplatz_id'),
                        message=f'validation error for data {feature_dict}: {e.to_dict()}',
                    ),
                )

        return self.apply_static_patches(static_parking_site_inputs), static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []
