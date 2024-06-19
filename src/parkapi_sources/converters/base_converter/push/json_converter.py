"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from parkapi_sources.converters.base_converter.push import PushConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput


class JsonConverter(PushConverter, ABC):
    @abstractmethod
    def handle_json(
        self,
        data: dict | list,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        pass
