"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import KonstanzParkingSiteInput, KonstanzParkingSitesInput


class KonstanzPullConverter(PullConverter):
    source_info = SourceInfo(
        uid='konstanz',
        name='Stadt Konstanz',
        source_url='https://services.gis.konstanz.digital/geoportal/rest/services/Fachdaten/Parkplaetze_Parkleitsystem'
        '/MapServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json',
        has_realtime_data=True,
    )
    konstanz_parking_sites_validator = DataclassValidator(KonstanzParkingSitesInput)
    konstanz_parking_site_validator = DataclassValidator(KonstanzParkingSiteInput)

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        parking_site_inputs, parking_site_errors = self._get_parking_site_inputs()

        static_parking_sites: list[StaticParkingSiteInput] = []
        for parking_site_input in parking_site_inputs:
            static_parking_sites.append(parking_site_input.to_static_parking_site())

        return static_parking_sites, parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        parking_site_inputs, parking_site_errors = self._get_parking_site_inputs()

        realtime_parking_sites: list[RealtimeParkingSiteInput] = []
        for parking_site_input in parking_site_inputs:
            realtime_parking_sites.append(parking_site_input.to_realtime_parking_site())

        return realtime_parking_sites, parking_site_errors

    def _get_parking_site_inputs(self) -> tuple[list[KonstanzParkingSiteInput], list[ImportParkingSiteException]]:
        parking_site_inputs: list[KonstanzParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        response = self.request_get(
            url=self.source_info.source_url,
            timeout=30,
        )

        parking_sites_input: KonstanzParkingSitesInput = self.konstanz_parking_sites_validator.validate(response.json())

        for parking_site_dict in parking_sites_input.features:
            try:
                parking_site_inputs.append(
                    self.konstanz_parking_site_validator.validate(parking_site_dict),
                )
            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=str(parking_site_dict.get('id')) if parking_site_dict.get('id') else None,
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )
        return parking_site_inputs, parking_site_errors


"""
There is an additional data source for this data at https://www.konstanz.de/konstanz/parkdaten/plc_info.txt . It seems,
that realtime data is integrated in their GeoServer, but if that changes at some point, we have a working import system
for the direct access. Their file format is quite cursed, as it's a CSV-style format with lots of whitespaces and
a Non-CSV header, so the JSON is much butter, but if you really want to use it, you will need this realtime validator:

@validataclass
class KonstanzRealtimeRowInput:
    uid: str = StringValidator()
    opening_status: KonstanzOpeningStatus = EnumValidator(KonstanzOpeningStatus)
    realtime_capacity: int = IntegerValidator(allow_strings=True, min_value=0)
    realtime_free_capacity: int = IntegerValidator(allow_strings=True, min_value=0)
    opening_time: time = TimeValidator(time_format=TimeFormat.NO_SECONDS)
    closing_time: time = TimeValidator(time_format=TimeFormat.NO_SECONDS)

    def to_realtime_parking_site_input(self, realtime_data_updated_at: datetime) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.uid,
            realtime_data_updated_at=realtime_data_updated_at,
            realtime_capacity=self.realtime_capacity,
            realtime_free_capacity=self.realtime_free_capacity,
            realtime_opening_status=self.opening_status.to_opening_status(),
        )


Together with this method for getting realtime data:


class KonstanzPullConverter(PullConverter):
    konstanz_realtime_validator = DataclassValidator(KonstanzRealtimeRowInput)

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        realtime_parking_site_errors: list[ImportParkingSiteException] = []

        response = self.request_get(
            url=self.source_info.source_url,
            auth=(self.config_helper.get('PARK_API_KONSTANZ_USER'), self.config_helper.get('PARK_API_KONSTANZ_PASSWORD')),
            timeout=30,
        )

        response_by_lines = response.text.splitlines()

        realtime_data_updated_at = (
            datetime.strptime(response_by_lines[1], 'Timestamp %d.%m.%Y, %H:%M:%S')
            .replace(tzinfo=ZoneInfo('Europe/Berlin'))
            .astimezone(tz=timezone.utc)
        )

        # Cut the first 4 lines because that's just a header
        csv_data = StringIO("\n".join(response_by_lines[4:]))

        reader = csv.reader(csv_data, delimiter=',')
        fields = ('uid', 'opening_status', 'realtime_capacity', 'realtime_free_capacity', 'opening_time', 'closing_time')
        for row in reader:
            input_dict = {key: value.strip() for key, value in dict(zip(fields, row)).items()}
            try:
                konstanz_input: KonstanzRealtimeRowInput = self.konstanz_realtime_validator.validate(input_dict)
                realtime_parking_site_inputs.append(
                    konstanz_input.to_realtime_parking_site_input(
                        realtime_data_updated_at=realtime_data_updated_at,
                    ),
                )
            except ValidationError as e:
                realtime_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('uid'),
                        message=f'validation error for {input_dict}: {e.to_dict()}',
                    ),
                )

        return realtime_parking_site_inputs, realtime_parking_site_errors
"""
