"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from .aachen import AachenPullConverter
from .aalen import AalenPullConverter
from .apcoa import ApcoaPullConverter
from .bahn_v2 import BahnV2PullConverter
from .base_converter import BaseConverter
from .basel import BaselPullConverter
from .bb_parkhaus import BBParkhausPushConverter
from .bfrk_bw import BfrkBwBikePullConverter, BfrkBwCarPullConverter
from .bielefeld import BielefeldPullConverter
from .bietigheim_bissingen import BietigheimBissingenPullConverter
from .bosch import (
    BoschKindingPullConverter,
    BoschRastpark24PullConverter,
    BoschSecureTruckParkingPullConverter,
    BoschThiersheimPullConverter,
)
from .bremen import BremenPullConverter
from .christophorus import ChristophorusPullConverter
from .dortmund import DortmundPullConverter
from .dresden import DresdenPullConverter
from .duesseldorf import DuesseldorfPullConverter
from .ellwangen import EllwangenPushConverter
from .ellwangen_sensit import EllwangenSensitPullConverter
from .erfurt import ErfurtPullConverter
from .esslingen import EsslingenPushConverter
from .frankfurt import FrankfurtPullConverter
from .freiburg import (
    FreiburgParkAndRideRealtimePullConverter,
    FreiburgParkAndRideStaticPullConverter,
    FreiburgPullConverter,
)
from .freiburg_disabled_sensors import FreiburgDisabledSensorsPullConverter
from .freiburg_disabled_static import FreiburgDisabledStaticPullConverter
from .freiburg_scanner import FreiburgScannerPullConverter
from .freiburg_vag_bike import FreiburgVAGBikePullConverter
from .friedrichshafen_easypark import FriedrichshafenEasyParkPushConverter
from .friedrichshafen_sensors import FriedrichshafenSensorsPullConverter
from .goldbeck import GoldbeckPushConverter
from .halle import HallePullConverter
from .hamburg_port_authority import HamburgPortAuthorityPullConverter
from .hanau import HanauPullConverter
from .heidelberg import HeidelbergPullConverter
from .heidelberg_disabled import HeidelbergDisabledPullConverter
from .heidelberg_easypark import HeidelbergEasyParkPullConverter
from .heilbronn import HeilbronnPullConverter
from .heilbronn_goldbeck import HeilbronnGoldbeckPullConverter
from .herrenberg import HerrenbergPullConverter
from .herrenberg_bike import HerrenbergBikePullConverter
from .huefner import HuefnerPushConverter
from .jena import JenaPullConverter
from .karlsruhe import (
    KarlsruheBikePullConverter,
    KarlsruheBusPullConverter,
    KarlsruheCaravanPullConverter,
    KarlsruheMotorcyclePullConverter,
    KarlsruheParkAndCarpoolPullConverter,
    KarlsruheParkAndRidePullConverter,
    KarlsruhePullConverter,
    KarlsruheTruckPullConverter,
)
from .karlsruhe_disabled import KarlsruheDisabledPullConverter
from .kassel import KasselPullConverter
from .keltern import KelternPushConverter
from .kienzler import (
    KienzlerBikeAndRidePullConverter,
    KienzlerKarlsruhePullConverter,
    KienzlerNeckarsulmPullConverter,
    KienzlerOffenburgPullConverter,
    KienzlerRadSafePullConverter,
    KienzlerStuttgartPullConverter,
    KienzlerUlmPullConverter,
    KienzlerVrnPullConverter,
    KienzlerVVSPullConverter,
)
from .koeln import KoelnPullConverter
from .konstanz import KonstanzPullConverter
from .konstanz_bike import KonstanzBikePullConverter
from .konstanz_disabled import KonstanzDisabledPullConverter
from .ladenburg_parkraumcheck import LadenburgParkraumcheckPushConverter
from .lbv_sh import LbvShPullConverter
from .magdeburg import MagdeburgPullConverter
from .magdeburg_ifak import MagdeburgIfakPullConverter
from .mannheim_buchen import BuchenPushConverter, MannheimPushConverter
from .nagold_bike import NagoldBikePushConverter
from .neckarsulm import NeckarsulmPushConverter
from .neckarsulm_bike import NeckarsulmBikePushConverter
from .nrw_disabled import NrwDisabledPullConverter
from .nuernberg import NuernbergPullConverter
from .oberstdorf import OberstdorfPullConverter
from .offenburg import OffenburgPullConverter
from .opendata_swiss import OpenDataSwissPullConverter
from .p_m_bw import PMBWPullConverter
from .p_m_sensade import PMSensadePullConverter
from .p_r_hessen import PRHessenPullConverter
from .park_raum_check import ParkRaumCheckKehlPushConverter, ParkRaumCheckSachsenheimPushConverter
from .pbw import PbwPullConverter
from .pforzheim import PforzheimPushConverter
from .pum_bw import PumBwPushConverter
from .radolfzell import RadolfzellPushConverter
from .radvis_bw import RadvisBwPullConverter
from .reutlingen import ReutlingenPushConverter
from .reutlingen_bike import ReutlingenBikePushConverter
from .reutlingen_disabled import ReutlingenDisabledPushConverter
from .stuttgart import StuttgartPushConverter
from .toll_collect import TollCollectPullConverter
from .trucklounge_ecopark import TruckloungeEcoparkPullConverter
from .ulm import UlmPullConverter
from .ulm_sensors import UlmSensorsPullConverter
from .velobrix import VelobrixPullConverter
from .vgn import VgnPullConverter
from .vrn_p_r import VrnParkAndRidePullConverter
from .vrs import VrsBondorfPullConverter, VrsKirchheimPullConverter, VrsNeustadtPullConverter, VrsVaihingenPullConverter
from .vrs_p_r import VrsParkAndRidePushConverter
from .wiesbaden import WiesbadenPullConverter
from .wuppertal import WuppertalPullConverter
from .zippel import ZippelPullConverter
from .zuerich import ZuerichPullConverter
