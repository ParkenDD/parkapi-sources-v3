"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from .geojson_inputs import (
    GeojsonBaseFeatureInput,
    GeojsonBaseFeaturePropertiesInput,
    GeojsonFeatureGeometryPointInput,
    GeojsonFeatureGeometryPolygonInput,
    GeojsonFeatureInput,
    GeojsonFeatureParkingSpotInput,
    GeojsonInput,
)
from .parking_restriction_inputs import ParkingRestrictionInput
from .parking_site_inputs import (
    CombinedParkingSiteInput,
    RealtimeParkingSiteInput,
    StaticParkingSiteInput,
    StaticParkingSitePatchInput,
    StaticPatchInput,
)
from .parking_spot_inputs import CombinedParkingSpotInput, RealtimeParkingSpotInput, StaticParkingSpotInput
from .source_info import SourceInfo
from .xlsx_inputs import ExcelOpeningTimeInput, ExcelStaticParkingSiteInput
