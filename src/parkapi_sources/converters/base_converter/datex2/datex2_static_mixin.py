"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from lxml import etree
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput


class Datex2StaticMixin(ABC):
    source_info: SourceInfo

    @abstractmethod
    def _transform_static_xml_to_static_input_dicts(self, xml_data: etree.Element) -> list[dict]:
        pass

    @property
    @abstractmethod
    def static_validator(self) -> DataclassValidator:
        pass

    @abstractmethod
    def get_uid_from_static_input_dict(self, input_dict: dict) -> str:
        pass

    def modify_static_parking_site_input(self, static_parking_site_input: StaticParkingSiteInput):
        """
        Can be overwritten by subclass.
        """

    def _handle_static_xml_data(
        self,
        static_xml_data: etree.Element,
    ) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        static_input_dicts: list[dict] = self._transform_static_xml_to_static_input_dicts(static_xml_data)

        for static_input_dict in static_input_dicts:
            try:
                static_item = self.static_validator.validate(static_input_dict)
                static_parking_site_input = static_item.to_static_parking_site_input()

                self.modify_static_parking_site_input(static_parking_site_input)

                static_parking_site_inputs.append(static_parking_site_input)

            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=self.get_uid_from_static_input_dict(static_input_dict),
                        message=str(e.to_dict()),
                    ),
                )
        return static_parking_site_inputs, static_parking_site_errors
