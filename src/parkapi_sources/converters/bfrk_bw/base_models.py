"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import IntegerValidator, NumericValidator, StringValidator, UrlValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ExternalIdentifierType
from parkapi_sources.models.parking_site_inputs import ExternalIdentifierInput
from parkapi_sources.validators import EmptystringNoneable


@validataclass
class BfrkBaseInput(ABC):
    objektid: int = IntegerValidator()
    # min / max are bounding box of Baden-Württemberg
    lat: Decimal = NumericValidator(min_value=Decimal('47.5'), max_value=Decimal('49.8'))
    lon: Decimal = NumericValidator(min_value=Decimal('7.5'), max_value=Decimal('10.5'))
    objekt_Foto: Optional[str] = EmptystringNoneable(UrlValidator()), Default(None)
    hst_dhid: Optional[str] = EmptystringNoneable(StringValidator(max_length=256)), Default(None)
    objekt_dhid: Optional[str] = EmptystringNoneable(StringValidator()), Default(None)
    infraid: str = StringValidator()
    osmlinks: Optional[str] = EmptystringNoneable(UrlValidator()), Default(None)
    gemeinde: Optional[str] = EmptystringNoneable(StringValidator()), Default(None)
    ortsteil: Optional[str] = EmptystringNoneable(StringValidator()), Default(None)

    @abstractmethod
    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        pass

    def get_static_parking_site_input_kwargs(self) -> dict:
        external_identifiers = []
        # Prevent url1|url2 link "lists"
        if self.osmlinks and '|' not in self.osmlinks:
            external_identifiers.append(
                ExternalIdentifierInput(
                    type=ExternalIdentifierType.OSM,
                    value=self.osmlinks,
                ),
            )
        if self.hst_dhid:
            external_identifiers.append(
                ExternalIdentifierInput(
                    type=ExternalIdentifierType.DHID,
                    value=self.hst_dhid,
                ),
            )

        if self.gemeinde and self.ortsteil:
            address = f'{self.ortsteil}, {self.gemeinde}'
        elif self.gemeinde:
            address = self.gemeinde
        elif self.ortsteil:
            address = self.ortsteil
        else:
            address = None

        return {
            'uid': self.infraid,
            'lat': self.lat,
            'lon': self.lon,
            'name': 'Parkplatz',
            'address': address,
            'photo_url': self.objekt_Foto,
            'external_identifiers': external_identifiers,
            'static_data_updated_at': datetime.now(tz=timezone.utc),
        }
