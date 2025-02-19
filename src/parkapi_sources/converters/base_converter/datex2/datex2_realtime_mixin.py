"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from lxml import etree
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo


class Datex2RealtimeMixin(ABC):
    source_info: SourceInfo

    @abstractmethod
    def _transform_realtime_xml_to_realtime_input_dicts(self, xml_data: etree.Element) -> list[dict]:
        pass

    @property
    @abstractmethod
    def realtime_validator(self) -> DataclassValidator:
        pass

    @abstractmethod
    def get_uid_from_realtime_input_dict(self, input_dict: dict) -> str:
        pass

    def _handle_realtime_xml_data(
        self,
        realtime_xml_data: etree.Element,
    ) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        realtime_parking_site_errors: list[ImportParkingSiteException] = []

        realtime_input_dicts: list[dict] = self._transform_realtime_xml_to_realtime_input_dicts(realtime_xml_data)

        for realtime_input_dict in realtime_input_dicts:
            try:
                realtime_item = self.realtime_validator.validate(realtime_input_dict)
                realtime_parking_site_inputs.append(realtime_item.to_realtime_parking_site_input())

            except ValidationError as e:
                realtime_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=self.get_uid_from_realtime_input_dict(realtime_input_dict),
                        message=str(e.to_dict()),
                    ),
                )

        return realtime_parking_site_inputs, realtime_parking_site_errors
