"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class SourceInfo:
    uid: str
    name: str
    has_realtime_data: Optional[bool]
    timezone: str = 'Europe/Berlin'
    public_url: Optional[str] = None
    source_url: Optional[str] = None
    attribution_license: Optional[str] = None
    attribution_url: Optional[str] = None
    attribution_contributor: Optional[str] = None

    def to_dict(self) -> dict:
        return {key: value for key, value in asdict(self).items() if value is not None}
