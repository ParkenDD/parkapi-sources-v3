"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod
from typing import Optional

from bs4 import BeautifulSoup
from bs4.element import Tag
from requests import Response
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo


class PullScraperMixin(ABC):
    source_info: SourceInfo
    realtime_parking_site_validator: DataclassValidator

    @abstractmethod
    def get_realtime_tags_and_params(self) -> tuple[list[Tag], dict]:
        pass

    @abstractmethod
    def realtime_tag_to_dict(self, tag: Tag, **kwargs) -> Optional[dict]:
        pass

    @abstractmethod
    def request_get(self, **kwargs) -> Response: ...

    def load_url_in_soup(self, url: Optional[str] = None):
        if url is None:
            url = self.source_info.public_url

        response = self.request_get(url=url, timeout=30)

        return BeautifulSoup(response.text, features='html.parser')

    def _get_scraped_realtime_parking_site_inputs_and_exceptions(
        self,
    ) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        tags, params = self.get_realtime_tags_and_params()
        for tag in tags:
            try:
                realtime_parking_site_dict = self.realtime_tag_to_dict(tag, **params)
            except Exception as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        message=f'Invalid data: {e}',
                    ),
                )
                continue

            # If realtime_parking_site_dict is None, we don't have a dataset to handle
            if realtime_parking_site_dict is None:
                continue

            try:
                realtime_parking_site_inputs.append(
                    self.realtime_parking_site_validator.validate(realtime_parking_site_dict),
                )
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=realtime_parking_site_dict.get('uid'),
                        message=f'Invallid data at uid {realtime_parking_site_dict.get("uid")}: {e.to_dict()}, '
                        f'data: {realtime_parking_site_dict}',
                    ),
                )

        return realtime_parking_site_inputs, import_parking_site_exceptions
