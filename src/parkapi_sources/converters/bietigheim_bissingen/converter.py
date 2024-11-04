"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import email
from csv import DictReader
from email import policy
from email.message import Message
from imaplib import IMAP4_SSL
from io import StringIO

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter, StaticGeojsonDataMixin
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import BietigheimBissingenInput


class BietigheimBissingenPullConverter(PullConverter, StaticGeojsonDataMixin):
    _imap_host: str = 'imap.strato.de'
    required_config_keys = ['PARK_API_BIETIGHEIM_BISSINGEN_USER', 'PARK_API_BIETIGHEIM_BISSINGEN_PASSWORD']
    bietigheim_bissingen_realtime_update_validator = DataclassValidator(BietigheimBissingenInput)
    source_info = SourceInfo(
        uid='bietigheim_bissingen',
        name='Stadt Bietigheim-Bissingen',
        public_url='https://www.bietigheim-bissingen.de/wirtschaft-verkehr-einkaufen/mobilitaet/',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_static_parking_site_inputs_and_exceptions(source_uid=self.source_info.uid)

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        for row_dict in self._parse_csv(self._get_data()):
            try:
                realtime_input = self.bietigheim_bissingen_realtime_update_validator.validate(row_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=row_dict.get('Name'),
                        message=f'Invalid data at uid {row_dict.get("Name")}: {e.to_dict()}, data: {row_dict}',
                    ),
                )
                continue

            realtime_parking_site_inputs.append(realtime_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _get_data(self) -> bytes:
        with IMAP4_SSL(self._imap_host) as imap_connection:
            imap_connection.login(
                self.config_helper.get('PARK_API_BIETIGHEIM_BISSINGEN_USER'),
                self.config_helper.get('PARK_API_BIETIGHEIM_BISSINGEN_PASSWORD'),
            )
            # Select default mailbox and get latest message uid
            _select_status, message_uid_list = imap_connection.select()
            if len(message_uid_list) == 0:
                raise ImportSourceException(
                    source_uid=self.source_info.uid,
                    message=f'No last email in inbox: {message_uid_list}.',
                )

            # Fetch the last mail
            message_uid = message_uid_list[0]
            imap_response: type[str, list] = imap_connection.fetch(message_uid, '(RFC822)')

        # Get raw_messages and check if there is one
        status, raw_messages = imap_response
        if len(raw_messages) == 0:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'No email in imap response although imap server provided status {status}.',
            )

        # If the raw message is no tuple, it's not a message
        raw_message: tuple[bytes, bytes] = raw_messages[0]
        if not isinstance(raw_message, tuple):
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'No valid email in imap response: {raw_message}.',
            )

        # The raw message has an envelope and a body, we just need the body
        _mail_envelope, mail_body = raw_message
        message: Message = email.message_from_bytes(mail_body, policy=policy.default.clone(linesep='\r\n'))

        return self._get_csv_bytes_from_message(message)

    @staticmethod
    def _parse_csv(csv_data: bytes) -> list[dict]:
        csv_rows = DictReader(StringIO(csv_data.decode('latin1')), delimiter=';')

        return list(csv_rows)

    def _get_csv_bytes_from_message(self, message: Message) -> bytes:
        for message_part in message.walk():
            if message_part.get_content_type() == 'application/octet-stream':
                return message_part.get_payload(decode=True)

        raise ImportSourceException(
            source_uid=self.source_info.uid,
            message=f'No valid attachment found in message {message}.',
        )
