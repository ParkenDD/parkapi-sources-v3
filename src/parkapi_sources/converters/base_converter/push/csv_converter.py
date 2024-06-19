"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import csv
from abc import ABC, abstractmethod
from io import StringIO
from typing import Any

from parkapi_sources.converters.base_converter.push import PushConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput


class CsvConverter(PushConverter, ABC):
    csv_delimiter = ';'

    def handle_csv_string(
        self,
        data: StringIO,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return self.handle_csv(list(csv.reader(data, delimiter=self.csv_delimiter)))

    def get_mapping_by_header(self, header_row: dict[str, str], row: list[Any]) -> dict[str, int]:
        mapping: dict[str, int] = {}
        for header_field, target_field in header_row.items():
            if header_field not in row:
                raise ImportSourceException(
                    source_uid=self.source_info.uid,
                    message=f'cannot find header key {header_field}',
                )
            mapping[target_field] = row.index(header_field)
        return mapping

    @abstractmethod
    def handle_csv(
        self,
        data: list[list],
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        pass
