"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from validataclass.validators import DataclassValidator

from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput
from parkapi_sources.util import ConfigHelper, DebugHelper


class BaseConverter(ABC):
    config_helper: ConfigHelper
    debug_helper: DebugHelper
    static_parking_site_validator = DataclassValidator(StaticParkingSiteInput)
    realtime_parking_site_validator = DataclassValidator(RealtimeParkingSiteInput)
    required_config_keys: list[str] = []

    def __init__(self, config_helper: ConfigHelper, debug_helper: DebugHelper):
        self.config_helper = config_helper
        self.debug_helper = debug_helper

    @property
    @abstractmethod
    def source_info(self) -> SourceInfo:
        pass

    def handle_debug_request_response(self, response):
        self.debug_helper.handle_request_response(self.source_info, response)
