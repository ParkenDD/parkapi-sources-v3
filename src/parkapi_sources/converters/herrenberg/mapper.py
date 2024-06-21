"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.herrenberg.validation import HerrenbergParkingSiteInput
from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkAndRideType


class Herrenbergmapper:
    def map_static_parking_site(self, herrenbergparkingsiteinput: HerrenbergParkingSiteInput) -> StaticParkingSiteInput:
        fee = None
        if herrenbergparkingsiteinput.fee_hours:
            fee = True
        herrenbergparkingsiteinput.ride = ParkAndRideType.NO

        disabled = 0
        if herrenbergparkingsiteinput.lot_type == 'Barrierefreier-Parkplatz':
            disabled = herrenbergparkingsiteinput.total
            herrenbergparkingsiteinput.total = 0

        return StaticParkingSiteInput(
            uid=herrenbergparkingsiteinput.id,
            name=herrenbergparkingsiteinput.name,
            lat=herrenbergparkingsiteinput.coords.lat,
            lon=herrenbergparkingsiteinput.coords.lng,
            operator_name="Stadt Herrenberg",
            address="Herrenberg " + herrenbergparkingsiteinput.address,
            capacity=herrenbergparkingsiteinput.total,
            description=herrenbergparkingsiteinput.notes.de,
            type=herrenbergparkingsiteinput.lot_type.to_parking_site_input_type(),
            park_and_ride_type=herrenbergparkingsiteinput.lot_type.to_parking_site_input_ride(),
            public_url=herrenbergparkingsiteinput.url,
            fee_description=herrenbergparkingsiteinput.fee_hours,
            opening_hours=herrenbergparkingsiteinput.opening_hours,
            has_fee=fee,
            capacity_disabled=disabled,

        )
