"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from .base_parking_inputs import RealtimeBaseParkingInput, StaticBaseParkingInput
from .enums import (
    ExternalIdentifierType,
    OpeningStatus,
    ParkAndRideType,
    ParkingAudience,
    ParkingSiteType,
    ParkingSpotStatus,
    ParkingSpotType,
    PurposeType,
    SourceStatus,
    SupervisionType,
)
from .geojson_inputs import (
    GeojsonBaseFeatureInput,
    GeojsonBaseFeaturePropertiesInput,
    GeojsonFeatureInput,
    GeojsonFeatureParkingSpotInput,
    GeojsonInput,
)
from .parking_site_inputs import (
    CombinedParkingSiteInput,
    ParkingSiteRestrictionInput,
    RealtimeParkingSiteInput,
    StaticParkingSiteInput,
    StaticParkingSitePatchInput,
    StaticPatchInput,
)
from .parking_spot_inputs import (
    CombinedParkingSpotInput,
    ParkingSpotRestrictionInput,
    RealtimeParkingSpotInput,
    StaticParkingSpotInput,
    StaticParkingSpotPatchInput,
)
from .shared_inputs import ExternalIdentifierInput, ParkingRestrictionInput
from .source_info import SourceInfo
from .xlsx_inputs import ExcelOpeningTimeInput, ExcelStaticParkingSiteInput
