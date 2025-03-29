"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""


class MissingConfigException(Exception):
    pass


class MissingConverterException(Exception):
    pass


class ImportException(Exception):
    source_uid: str
    message: str
    data: dict | None

    def __init__(self, source_uid: str, message: str, data: dict | None = None):
        self.source_uid = source_uid
        self.message = message
        self.data = data

    def __repr__(self) -> str:
        result = f'{self.__class__.__name__} {self.source_uid}: {self.message}'
        if self.data:
            result += f'; data: {self.data}'
        return result

    def __str__(self) -> str:
        result = f'{self.__class__.__name__} {self.source_uid}: {self.message}'
        if self.data:
            result += f'; data: {self.data}'
        return result


class ImportSourceException(ImportException):
    pass


class ImportParkingSiteException(ImportException):
    parking_site_uid: str | None = None

    def __init__(self, *args, parking_site_uid: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parking_site_uid = parking_site_uid

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} {self.source_uid} {self.parking_site_uid}: {self.message}'

    def __str__(self) -> str:
        return f'{self.__class__.__name__} {self.source_uid} {self.parking_site_uid}: {self.message}'


class ImportParkingSpotException(ImportException):
    parking_spot_uid: str | None = None

    def __init__(self, *args, parking_spot_uid: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parking_spot_uid = parking_spot_uid

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} {self.source_uid} {self.parking_spot_uid}: {self.message}'

    def __str__(self) -> str:
        return f'{self.__class__.__name__} {self.source_uid} {self.parking_spot_uid}: {self.message}'
