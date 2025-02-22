"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from requests import Response
from validataclass.validators import DataclassValidator

from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput
from parkapi_sources.util import ConfigHelper, RequestHelper


class BaseConverter(ABC):
    config_helper: ConfigHelper
    request_helper: RequestHelper
    static_parking_site_validator = DataclassValidator(StaticParkingSiteInput)
    realtime_parking_site_validator = DataclassValidator(RealtimeParkingSiteInput)
    required_config_keys: list[str] = []

    def __init__(self, config_helper: ConfigHelper, request_helper: RequestHelper):
        self.config_helper = config_helper
        self.request_helper = request_helper

    @property
    @abstractmethod
    def source_info(self) -> SourceInfo:
        pass

    def request_get(self, **kwargs) -> Response:
        return self.request_helper.get(source_info=self.source_info, **kwargs)

    def request_post(self, **kwargs) -> Response:
        return self.request_helper.post(source_info=self.source_info, **kwargs)

    def request_put(self, **kwargs) -> Response:
        return self.request_helper.put(source_info=self.source_info, **kwargs)

    def request_patch(self, **kwargs) -> Response:
        return self.request_helper.patch(source_info=self.source_info, **kwargs)

    def request_delete(self, **kwargs) -> Response:
        return self.request_helper.delete(source_info=self.source_info, **kwargs)
