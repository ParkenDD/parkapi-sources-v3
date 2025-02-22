"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional, Type

from .converters import (
    AachenPullConverter,
    ApcoaPullConverter,
    BahnV2PullConverter,
    BaseConverter,
    BfrkBwBikePushConverter,
    BfrkBwCarPushConverter,
    BietigheimBissingenPullConverter,
    BuchenPushConverter,
    EllwangenPushConverter,
    FreiburgPullConverter,
    GoldbeckPushConverter,
    HeidelbergPullConverter,
    HerrenbergBikePullConverter,
    HerrenbergPullConverter,
    HuefnerPushConverter,
    KarlsruheBikePullConverter,
    KarlsruhePullConverter,
    KienzlerBikeAndRidePullConverter,
    KienzlerKarlsruhePullConverter,
    KienzlerNeckarsulmPullConverter,
    KienzlerOffenburgPullConverter,
    KienzlerRadSafePullConverter,
    KienzlerStuttgartPullConverter,
    KienzlerVrnPullConverter,
    KienzlerVVSPullConverter,
    KonstanzBikePushConverter,
    KonstanzPullConverter,
    MannheimPushConverter,
    NeckarsulmBikePushConverter,
    NeckarsulmPushConverter,
    OpenDataSwissPullConverter,
    PbwPullConverter,
    PforzheimPushConverter,
    PMBWPullConverter,
    PumBwPushConverter,
    RadvisBwPullConverter,
    ReutlingenBikePushConverter,
    ReutlingenPushConverter,
    StuttgartPushConverter,
    UlmPullConverter,
    VelobrixPullConverter,
    VrnParkAndRidePullConverter,
    VrsBondorfPullConverter,
    VrsKirchheimPullConverter,
    VrsNeustadtPullConverter,
    VrsParkAndRidePushConverter,
    VrsVaihingenPullConverter,
)
from .converters.base_converter.pull import PullConverter
from .converters.base_converter.push import PushConverter
from .exceptions import MissingConfigException, MissingConverterException
from .util import ConfigHelper, RequestHelper


class ParkAPISources:
    converter_classes: list[Type[BaseConverter]] = [
        AachenPullConverter,
        ApcoaPullConverter,
        BahnV2PullConverter,
        BfrkBwBikePushConverter,
        BfrkBwCarPushConverter,
        BietigheimBissingenPullConverter,
        EllwangenPushConverter,
        GoldbeckPushConverter,
        BuchenPushConverter,
        FreiburgPullConverter,
        HeidelbergPullConverter,
        HerrenbergBikePullConverter,
        HerrenbergPullConverter,
        HuefnerPushConverter,
        KarlsruheBikePullConverter,
        KarlsruhePullConverter,
        KienzlerBikeAndRidePullConverter,
        KienzlerVVSPullConverter,
        KienzlerKarlsruhePullConverter,
        KienzlerNeckarsulmPullConverter,
        KienzlerOffenburgPullConverter,
        KienzlerRadSafePullConverter,
        KienzlerStuttgartPullConverter,
        KienzlerVrnPullConverter,
        KonstanzBikePushConverter,
        KonstanzPullConverter,
        MannheimPushConverter,
        NeckarsulmBikePushConverter,
        NeckarsulmPushConverter,
        OpenDataSwissPullConverter,
        PbwPullConverter,
        PforzheimPushConverter,
        PMBWPullConverter,
        PumBwPushConverter,
        RadvisBwPullConverter,
        ReutlingenPushConverter,
        ReutlingenBikePushConverter,
        StuttgartPushConverter,
        UlmPullConverter,
        VrnParkAndRidePullConverter,
        VelobrixPullConverter,
        VrsBondorfPullConverter,
        VrsKirchheimPullConverter,
        VrsNeustadtPullConverter,
        VrsParkAndRidePushConverter,
        VrsVaihingenPullConverter,
    ]
    config_helper: ConfigHelper
    converter_by_uid: dict[str, BaseConverter]

    def __init__(
        self,
        config: Optional[dict] = None,
        converter_uids: Optional[list[str]] = None,
        no_pull_converter: bool = False,
        no_push_converter: bool = False,
    ):
        self.config_helper = ConfigHelper(config=config)
        self.request_helper = RequestHelper(config_helper=self.config_helper)
        self.converter_by_uid = {}

        converter_classes_by_uid: dict[str, Type[BaseConverter]] = {
            converter_class.source_info.uid: converter_class for converter_class in self.converter_classes
        }

        if converter_uids is None:
            converter_uids = list(converter_classes_by_uid.keys())

        for converter_uid in converter_uids:
            if no_push_converter and issubclass(converter_classes_by_uid[converter_uid], PushConverter):
                continue

            if no_pull_converter and issubclass(converter_classes_by_uid[converter_uid], PullConverter):
                continue

            if converter_uid not in converter_classes_by_uid.keys():
                raise MissingConverterException(f'Converter {converter_uid} does not exist.')

            self.converter_by_uid[converter_uid] = converter_classes_by_uid[converter_uid](
                config_helper=self.config_helper,
                request_helper=self.request_helper,
            )

    def check_credentials(self):
        for converter in self.converter_by_uid.values():
            for config_key in converter.required_config_keys:
                if self.config_helper.get(config_key) is None:
                    raise MissingConfigException(f'Config key {config_key} is missing.')
