"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from decimal import Decimal

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    ListValidator,
    Noneable,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import ExternalIdentifierInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ExternalIdentifierType
from parkapi_sources.validators import EmptystringNoneable


@validataclass
class BfrkBaseInput(ABC):
    # min / max are bounding box of Baden-Württemberg
    lat: Decimal = NumericValidator(min_value=Decimal('47.5'), max_value=Decimal('49.8'))
    lon: Decimal = NumericValidator(min_value=Decimal('7.5'), max_value=Decimal('10.5'))
    objekt_Foto: str | None = EmptystringNoneable(UrlValidator()), Default(None)
    hst_dhid: str = StringValidator(max_length=256)
    objekt_dhid: str | None = EmptystringNoneable(StringValidator()), Default(None)
    infraid: str = StringValidator()
    osmlinks: list[str] | None = Noneable(ListValidator(EmptystringNoneable(UrlValidator()))), Default(None)
    gemeinde: str | None = EmptystringNoneable(StringValidator()), Default(None)
    ortsteil: str | None = EmptystringNoneable(StringValidator()), Default(None)
    koordinatenqualitaet: str | None = EmptystringNoneable(StringValidator()), Default(None)

    @abstractmethod
    def to_static_parking_site_input(self) -> StaticParkingSiteInput | None:
        pass

    def get_static_parking_site_input_kwargs(self) -> dict:
        return {
            'uid': self.infraid,
            'lat': self.lat,
            'lon': self.lon,
            'name': 'Parkplatz',
            'address': self._get_address(),
            'photo_url': self.objekt_Foto,
            'external_identifiers': self._get_external_identifiers(),
            'static_data_updated_at': datetime.now(tz=timezone.utc),
            'has_realtime_data': False,
        }

    def _get_address(self) -> str | None:
        """
        Returns a normalized address string by combining the values of 'gemeinde' and 'ortsteil',
        with a few additional checks to avoid nested parentheses and duplication.

        Examples:

        gemeinde 'Stuttgart' + ortsteil None -> address 'Stuttgart'
        gemeinde None + ortsteil 'Stuttgart' -> address 'Stuttgart'
        gemeinde 'Basel' + ortsteil 'Basel' -> address 'Basel'
        gemeinde 'Renningen' + ortsteil 'Malmsheim' -> address 'Renningen (Malmsheim)'
        gemeinde 'Geislingen an der Steige' + ortsteil 'Geislingen (Steige)' -> address 'Geislingen an der Steige'
        gemeinde 'Leonberg' + ortsteil 'Höfingen (Württ)' -> address 'Leonberg (Höfingen)'
        """
        if self.gemeinde and self.ortsteil and self.ortsteil != self.gemeinde:
            # remove any part in parentheses from 'ortsteil' value, and strip trailing whitespace
            self.ortsteil = re.sub(pattern=r'\(.*\)', repl='', string=str(self.ortsteil)).strip()
            # if the first word is identical, don't add ortsteil:
            if self.gemeinde.split()[0] == self.ortsteil.split()[0]:
                return self.gemeinde
            else:
                return f'{self.gemeinde} ({self.ortsteil})'
        elif self.gemeinde:
            return self.gemeinde
        elif self.ortsteil:
            return self.ortsteil
        return None

    def _get_external_identifiers(self) -> list[ExternalIdentifierInput]:
        external_identifiers: list[ExternalIdentifierInput] = []
        if self.osmlinks:
            [
                external_identifiers.append(
                    ExternalIdentifierInput(
                        type=ExternalIdentifierType.OSM,
                        value=osmlink,
                    ),
                )
                for osmlink in self.osmlinks
            ]
        if self.hst_dhid:
            external_identifiers.append(
                ExternalIdentifierInput(
                    type=ExternalIdentifierType.DHID,
                    value=self.hst_dhid,
                ),
            )
        return external_identifiers
