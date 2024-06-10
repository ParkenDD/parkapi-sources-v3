"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from validataclass.dataclasses import validataclass
from validataclass.validators import IntegerValidator, StringValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ExternalIdentifierType
from parkapi_sources.models.parking_site_inputs import ExternalIdentifierInput
from parkapi_sources.validators import ExcelNoneable, GermanDecimalValidator


@validataclass
class BfrkBaseRowInput:
    uid: str = StringValidator()
    name: str = StringValidator()
    # min / max are bounding box of Baden-Württemberg
    lat: Decimal = GermanDecimalValidator(min_value=Decimal('47.5'), max_value=Decimal('49.8'))
    lon: Decimal = GermanDecimalValidator(min_value=Decimal('7.5'), max_value=Decimal('10.5'))
    capacity: int = IntegerValidator(allow_strings=True)
    identifier_dhid: str = StringValidator()
    identifier_osm: str = StringValidator()
    photo_url: Optional[str] = ExcelNoneable(StringValidator())

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        external_identifiers = []
        if self.identifier_osm:
            external_identifiers.append(
                ExternalIdentifierInput(
                    type=ExternalIdentifierType.OSM,
                    value=self.identifier_osm,
                ),
            )
        if self.identifier_dhid:
            external_identifiers.append(
                ExternalIdentifierInput(
                    type=ExternalIdentifierType.DHID,
                    value=self.identifier_dhid,
                ),
            )

        return StaticParkingSiteInput(
            uid=self.uid,
            name=self.name,
            lat=self.lat,
            lon=self.lon,
            address='',
            capacity=self.capacity,
            photo_url=self.photo_url,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            external_identifiers=external_identifiers,
        )
