"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import GeojsonInput, SourceInfo, StaticParkingSiteInput

from .validator import FreiburgScannerFeatureInput


class FreiburgScannerPullConverter(ParkingSitePullConverter):
    source_info = SourceInfo(
        uid='freiburg_scanner',
        name='Freiburg Scanner',
        source_url='https://geoportal.freiburg.de/wfs/digit_parken/digit_parken?REQUEST=GetFeature&SRSNAME=EPSG:4326'
        '&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=parkkartierung_mercedes_kanten&OUTPUTFORMAT=geojson',
        has_realtime_data=False,
    )
    geojson_validator = DataclassValidator(GeojsonInput)
    freiburg_scanner_feature_validator = DataclassValidator(FreiburgScannerFeatureInput)

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_sites: list[StaticParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        static_data_updated_at = datetime.now(timezone.utc)
        response = self.request_get(
            url=self.source_info.source_url,
            timeout=30,
        )

        parking_sites_input: GeojsonInput = self.geojson_validator.validate(response.json())

        for parking_site_dict in parking_sites_input.features:
            try:
                freiburg_parking_site_input = self.freiburg_scanner_feature_validator.validate(parking_site_dict)
                static_parking_site = freiburg_parking_site_input.to_static_parking_site(
                    static_data_updated_at=static_data_updated_at,
                )
                if static_parking_site is None:
                    continue

                static_parking_sites.append(static_parking_site)

            except ValidationError as e:
                uid: str | None = parking_site_dict.get('properties', {}).get('id')
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=str(uid) if uid else None,
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return static_parking_sites, parking_site_errors
