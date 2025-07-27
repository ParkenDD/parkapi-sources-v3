"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter, StaticGeojsonDataMixin
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import GeojsonInput, RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import (
    FreiburgBaseFeatureInput,
    FreiburgFeatureInput,
    FreiburgParkAndRideRealtimeFeatureInput,
    FreiburgParkAndRideStaticFeatureInput,
)


class FreiburgBasePullConverter(ParkingSitePullConverter, StaticGeojsonDataMixin, ABC):
    geojson_validator = DataclassValidator(GeojsonInput)
    freiburg_feature_validator: DataclassValidator

    def _get_raw_features(self) -> tuple[list[FreiburgBaseFeatureInput], list[ImportParkingSiteException]]:
        freiburg_inputs: list[FreiburgBaseFeatureInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(url=self.source_info.source_url, timeout=30)
        response_data = response.json()

        try:
            realtime_input: GeojsonInput = self.geojson_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid Input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

        for update_dict in realtime_input.features:
            try:
                freiburg_inputs.append(self.freiburg_feature_validator.validate(update_dict))
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=update_dict.get('properties').get('obs_parkid'),
                        message=f'Invalid data at uid {update_dict.get("properties").get("obs_parkid")}: '
                        f'{e.to_dict()}, data: {update_dict}',
                    ),
                )
                continue

        return freiburg_inputs, import_parking_site_exceptions

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        feature_inputs, import_parking_site_exceptions = self._get_raw_features()

        for feature_input in feature_inputs:
            static_parking_site_inputs.append(
                feature_input.to_static_parking_site_input(),
            )

        return self.apply_static_patches(static_parking_site_inputs), import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        feature_inputs, import_parking_site_exceptions = self._get_raw_features()

        for feature_input in feature_inputs:
            realtime_parking_site_input = feature_input.to_realtime_parking_site_input()
            if realtime_parking_site_input is not None:
                realtime_parking_site_inputs.append(realtime_parking_site_input)

        return realtime_parking_site_inputs, import_parking_site_exceptions


class FreiburgPullConverter(FreiburgBasePullConverter):
    freiburg_feature_validator = DataclassValidator(FreiburgFeatureInput)
    source_info = SourceInfo(
        uid='freiburg',
        name='Stadt Freiburg',
        public_url='https://www.freiburg.de/pb/,Lde/231355.html',
        source_url='https://geoportal.freiburg.de/wfs/gdm_pls/gdm_plslive?request=getfeature&service=wfs&version=1.1.0&typename=pls'
        '&outputformat=geojson&srsname=epsg:4326',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Freiburg',
        attribution_license='dl-de/by-2-0',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs, import_parking_site_exceptions = (
            self._get_static_parking_site_inputs_and_exceptions(
                source_uid=self.source_info.uid,
            )
        )

        realtime_freiburg_inputs: list[FreiburgFeatureInput]
        realtime_freiburg_inputs, import_realtime_parking_site_exceptions = self._get_raw_features()
        import_parking_site_exceptions += import_realtime_parking_site_exceptions

        static_parking_site_inputs_by_uid: dict[str, StaticParkingSiteInput] = {}
        for static_parking_site_input in static_parking_site_inputs:
            static_parking_site_inputs_by_uid[static_parking_site_input.uid] = static_parking_site_input

        for realtime_freiburg_input in realtime_freiburg_inputs:
            # If the uid is not known in our static data: ignore the realtime data
            parking_site_uid = str(realtime_freiburg_input.properties.obs_parkid)
            if parking_site_uid not in static_parking_site_inputs_by_uid:
                continue

            # Extend static data with realtime data
            realtime_freiburg_input.extend_static_parking_site_input(
                static_parking_site_inputs_by_uid[parking_site_uid],
            )

        return self.apply_static_patches(static_parking_site_inputs), import_parking_site_exceptions


class FreiburgParkAndRideStaticPullConverter(FreiburgBasePullConverter):
    freiburg_feature_validator = DataclassValidator(FreiburgParkAndRideStaticFeatureInput)
    source_info = SourceInfo(
        uid='freiburg_p_r_static',
        name='Stadt Freiburg: Park and Ride Statische Parkplätze',
        source_url='https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?SERVICE=WFS&REQUEST=GetFeature&SRSNAME=EPSG:4326'
        '&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=parkandride&OUTPUTFORMAT=geojson&crs=4326',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Freiburg',
        attribution_license='dl-de/by-2-0',
        has_realtime_data=True,
    )


class FreiburgParkAndRideRealtimePullConverter(FreiburgBasePullConverter):
    freiburg_feature_validator = DataclassValidator(FreiburgParkAndRideRealtimeFeatureInput)
    source_info = SourceInfo(
        uid='freiburg_p_r_sensors',
        name='Stadt Freiburg: Park and Ride Parkplätze mit Sensoren',
        source_url='https://geoportal.freiburg.de/wfs/gdm_pls/gdm_pls?SERVICE=WFS&REQUEST=GetFeature&SRSNAME=EPSG:4326'
        '&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=parkandride_aktuell&OUTPUTFORMAT=geojson&crs=4326',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Freiburg',
        attribution_license='dl-de/by-2-0',
        has_realtime_data=True,
    )
