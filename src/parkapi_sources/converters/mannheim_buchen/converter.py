"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter.push import ParkApiConverter
from parkapi_sources.models import SourceInfo


class MannheimPushConverter(ParkApiConverter):
    source_info = SourceInfo(
        uid='mannheim',
        name='Stadt Mannheim',
        public_url='https://www.parken-mannheim.de',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )


class BuchenPushConverter(ParkApiConverter):
    source_info = SourceInfo(
        uid='buchen',
        name='Stadt Buchen',
        public_url='https://www.buchen.de/ueber-buchen/kostenlos-parken.html',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )
