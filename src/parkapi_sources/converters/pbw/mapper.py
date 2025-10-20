"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from parkapi_sources.models import (
    ParkingAudience,
    ParkingSiteRestrictionInput,
    RealtimeParkingSiteInput,
    StaticParkingSiteInput,
)

from .validation import PbwParkingSiteDetailInput, PbwRealtimeInput


class PbwMapper:
    def map_static_parking_site(self, parking_site_detail_input: PbwParkingSiteDetailInput) -> StaticParkingSiteInput:
        max_height = None
        if parking_site_detail_input.ausstattung.einfahrtshoehe:
            max_height = int(parking_site_detail_input.ausstattung.einfahrtshoehe * 100)

        # We use StaticParkingSiteInput without validation because we validated the data before
        static_parking_site_input = StaticParkingSiteInput(
            uid=str(parking_site_detail_input.id),
            name=parking_site_detail_input.objekt.name,
            operator_name='Parkraumgesellschaft Baden-Württemberg mbH',
            public_url=f'https://www.pbw.de/?menu=parkplatz-finder&search=*{str(parking_site_detail_input.id)}',
            static_data_updated_at=datetime.now(tz=timezone.utc),
            address=(
                f'{parking_site_detail_input.objekt.strasse}, '
                f'{parking_site_detail_input.objekt.plz} {parking_site_detail_input.objekt.ort}'
            ),
            type=parking_site_detail_input.objekt.art_lang.to_parking_site_type_input(),
            max_height=max_height,
            # TODO: any way to create a fee_description or has_fee?
            # TODO: which field is maps to is_supervised?
            has_realtime_data=parking_site_detail_input.dynamisch.kurzparker_frei is not None,
            lat=parking_site_detail_input.position.latitude,
            lon=parking_site_detail_input.position.longitude,
            capacity=parking_site_detail_input.stellplaetze.gesamt,
            # TODO: opening_hours
        )

        restrictions: list[ParkingSiteRestrictionInput] = []
        if parking_site_detail_input.stellplaetze.behinderte is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.DISABLED,
                    capacity=parking_site_detail_input.stellplaetze.behinderte,
                ),
            )
        if parking_site_detail_input.stellplaetze.frauen is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.WOMEN,
                    capacity=parking_site_detail_input.stellplaetze.frauen,
                ),
            )
        if parking_site_detail_input.stellplaetze.familien is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.FAMILY,
                    capacity=parking_site_detail_input.stellplaetze.familien,
                ),
            )
        if parking_site_detail_input.stellplaetze.elektrofahrzeuge is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                    capacity=parking_site_detail_input.stellplaetze.elektrofahrzeuge,
                ),
            )
        if len(restrictions):
            static_parking_site_input.restrictions = restrictions

        return static_parking_site_input

    def map_realtime_parking_site(self, realtime_input: PbwRealtimeInput) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=str(realtime_input.id),
            realtime_data_updated_at=datetime.now(tz=timezone.utc),
            realtime_free_capacity=realtime_input.dynamisch.kurzparker_frei,
        )
