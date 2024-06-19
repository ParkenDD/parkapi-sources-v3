"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from validataclass.validators import DataclassValidator

from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput
from parkapi_sources.util import ConfigHelper


class BaseConverter(ABC):
    config_helper: ConfigHelper
    static_parking_site_validator = DataclassValidator(StaticParkingSiteInput)
    realtime_parking_site_validator = DataclassValidator(RealtimeParkingSiteInput)
    required_config_keys: list[str] = []

    def __init__(self, config_helper: ConfigHelper):
        self.config_helper = config_helper

    @property
    @abstractmethod
    def source_info(self) -> SourceInfo:
        pass
