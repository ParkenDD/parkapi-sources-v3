"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC, abstractmethod

from openpyxl.cell import Cell
from openpyxl.workbook import Workbook
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.push import PushConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import (
    ExcelOpeningTimeInput,
    ExcelStaticParkingSiteInput,
    RealtimeParkingSiteInput,
    SourceInfo,
    StaticParkingSiteInput,
)


class XlsxConverter(PushConverter, ABC):
    static_parking_site_validator = DataclassValidator(ExcelStaticParkingSiteInput)
    excel_opening_time_validator = DataclassValidator(ExcelOpeningTimeInput)

    header_row: dict[str, str] = {}
    source_info: SourceInfo

    @abstractmethod
    def handle_xlsx(
        self,
        workbook: Workbook,
    ) -> tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        pass

    def get_mapping_by_header(self, row: tuple[Cell, ...]) -> dict[str, int]:
        row_values = [cell.value for cell in row]
        mapping: dict[str, int] = {}
        for header_col, target_field in self.header_row.items():
            if header_col not in row_values:
                raise ImportSourceException(
                    source_uid=self.source_info.uid,
                    message=f'cannot find header key {header_col}',
                )
            mapping[target_field] = row_values.index(header_col)
        return mapping
