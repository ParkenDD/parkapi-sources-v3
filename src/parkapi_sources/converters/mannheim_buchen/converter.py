"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.push import ParkApiConverter
from parkapi_sources.models import PurposeType, SourceInfo, StaticParkingSiteInput


@validataclass
class MannheimStaticParkingSiteInput(StaticParkingSiteInput):
    purpose: PurposeType = Default(PurposeType.CAR)


class MannheimPushConverter(ParkApiConverter):
    static_parking_site_validator = DataclassValidator(MannheimStaticParkingSiteInput)

    source_info = SourceInfo(
        uid='mannheim',
        name='Stadt Mannheim',
        public_url='https://www.parken-mannheim.de',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )


class BuchenPushConverter(ParkApiConverter):
    static_parking_site_validator = DataclassValidator(MannheimStaticParkingSiteInput)

    source_info = SourceInfo(
        uid='buchen',
        name='Stadt Buchen',
        public_url='https://www.buchen.de/ueber-buchen/kostenlos-parken.html',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )
