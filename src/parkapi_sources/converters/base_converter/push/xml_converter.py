"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from lxml.etree import Element

from parkapi_sources.converters.base_converter.push import PushConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.util import XMLHelper


class XmlConverter(PushConverter, ABC):
    xml_helper = XMLHelper()

    @abstractmethod
    def handle_xml(
        self,
        root: Element,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        pass
