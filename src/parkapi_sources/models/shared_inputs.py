"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from isodate import Duration
from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.validators import EnumValidator, Noneable, StringValidator

from parkapi_sources.models.enums import ExternalIdentifierType, ParkingAudience
from parkapi_sources.validators.iso_duration_validator import IsoDurationValidator


@validataclass
class ParkingRestrictionInput(ValidataclassMixin):
    type: ParkingAudience | None = Noneable(EnumValidator(ParkingAudience)), Default(None)
    hours: str | None = Noneable(StringValidator()), Default(None)
    max_stay: Duration | None = Noneable(IsoDurationValidator()), Default(None)


@validataclass
class ExternalIdentifierInput(ValidataclassMixin):
    type: ExternalIdentifierType = EnumValidator(ExternalIdentifierType)
    value: str = StringValidator(max_length=256)
