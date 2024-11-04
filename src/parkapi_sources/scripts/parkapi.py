"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Optional

from parkapi_sources import ParkAPISources
from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput
from parkapi_sources.util import DefaultJSONEncoder


def main():
    parser = argparse.ArgumentParser(
        prog='Park-API',
        description='This library helps to get static and realtime parking site data. Outputs all sources to stdout per default. Uses '
        'env vars for config.',
    )
    parser.add_argument('-s', '--source', dest='sources', nargs='+', help='Limit to specific sources.')
    parser.add_argument(
        '-t',
        '--type',
        dest='output_type',
        choices=['json', 'geojson'],
        default='json',
        help='Output format.',
    )
    parser.add_argument(
        '-d',
        '--directory',
        dest='output_directory',
        help='Directory where data should be saved in one file per source.',
    )
    parser.add_argument(
        '-f',
        '--file',
        dest='output_file',
        help='Single File where all data should be saved in one file.',
    )
    parser.add_argument(
        '-gtd',
        '--geojson-template-directory',
        dest='geojson_template_directory',
        help='Instead of loading GeoJSON template files from Github, you can load it from a local directory.',
    )

    args = parser.parse_args()

    output_file_path: Optional[Path] = None
    if args.output_file is not None:
        output_file_path = Path(args.output_file)
        if not output_file_path.parent.is_dir():
            raise ValueError('Output file directory has to exist.')

    output_directory: Optional[Path] = None
    if args.output_directory is not None:
        output_directory = Path(args.output_directory)
        if not output_directory.is_dir():
            raise ValueError('Output directory has to exist.')

    geojson_template_directory: Optional[Path] = None
    if args.geojson_template_directory is not None:
        geojson_template_directory = Path(args.geojson_template_directory)
        if not geojson_template_directory.is_dir():
            raise ValueError('GeoJSON template directory has be an directory.')

    if output_file_path is not None and output_directory is not None:
        raise ValueError('output directory and output file cannot be set at the same time.')

    # Load config variables from environment
    config = dict(os.environ)
    if geojson_template_directory is not None:
        config['STATIC_GEOJSON_BASE_PATH'] = geojson_template_directory

    parkapi_sources = ParkAPISources(config=config, converter_uids=args.sources, no_push_converter=True)

    # Check if all credentials are given by env vars.
    parkapi_sources.check_credentials()

    # Initiate result dict. We collect all info in one dict because we decide later if we output it to stdout, to a single file or to
    # multiple files. The list has always two entries, one first is a StaticParkingSiteInput, second an Optional[RealtimeParkingSiteInput].
    result: dict[
        str, tuple[SourceInfo, dict[str, list[Optional[StaticParkingSiteInput | RealtimeParkingSiteInput]]]]
    ] = {}
    for source_uid, converter in parkapi_sources.converter_by_uid.items():
        result[source_uid] = (converter.source_info, {})

    # Iterate over sources and get all the data
    for source_uid, (_, source_results) in result.items():
        converter: PullConverter = parkapi_sources.converter_by_uid[source_uid]  # type: ignore

        static_parking_site_inputs, _ = converter.get_static_parking_sites()
        for static_parking_site_input in static_parking_site_inputs:
            source_results[static_parking_site_input.uid] = [static_parking_site_input, None]

        realtime_parking_site_inputs, _ = converter.get_realtime_parking_sites()
        for realtime_parking_site_input in realtime_parking_site_inputs:
            # If the realtime uid does not have a corresponding static dataset: ignore the realtime dataset
            if realtime_parking_site_input.uid not in result[source_uid][1]:
                continue
            source_results[realtime_parking_site_input.uid][1] = realtime_parking_site_input

    if args.output_type == 'geojson':
        if output_directory is None:
            # If we don't have an output directory, we have to create a single GeoJSON file with all features
            output_geojson_features: list[dict] = []
            for source_info, source_results in result.values():
                output_geojson_features += source_results_to_geojson_feature(source_info, source_results)

            output_geojson = json_dump(geojson_collection(output_geojson_features))
            if output_file_path is None:
                print(output_geojson)  # noqa: T201
            else:
                with output_file_path.open('w') as output_file:
                    output_file.write(output_geojson)
            return

        # If we have an output directory, we have to split the GeoJSON data up in separate files
        for source_info, source_results in result.values():
            geojson_file_path = Path(output_directory, f'{source_info.uid}.geojson')
            output_geojson_features = source_results_to_geojson_feature(source_info, source_results)
            output_geojson = json_dump(geojson_collection(output_geojson_features))
            with geojson_file_path.open('w') as geojson_file:
                geojson_file.write(output_geojson)

        return

    if output_directory is None:
        # If we don't have an output directory, we have to create a single JSON file with all the data
        output_dicts: list[dict] = []
        for source_info, source_results in result.values():
            output_dicts.append(source_results_to_dict(source_info, source_results))

        output_json = json_dump(output_dicts)
        if output_file_path is None:
            print(output_json)  # noqa: T201
        else:
            with output_file_path.open('w') as output_file:
                output_file.write(output_json)
        return

    for source_info, source_results in result.values():
        geojson_file_path = Path(output_directory, f'{source_info.uid}.json')
        output_dict = source_results_to_dict(source_info, source_results)
        output_json = json_dump(output_dict)

        with geojson_file_path.open('w') as geojson_file:
            geojson_file.write(output_json)


def parking_site_inputs_to_geojson_feature(
    source_info: SourceInfo,
    static_parking_site_input: StaticParkingSiteInput,
    realtime_parking_site_input: Optional[RealtimeParkingSiteInput] = None,
) -> dict:
    return {
        'geometry': {
            'type': 'Point',
            'coordinates': [float(static_parking_site_input.lon), float(static_parking_site_input.lat)],
        },
        'properties': {
            **static_parking_site_input.to_dict(),
            **({} if realtime_parking_site_input is None else realtime_parking_site_input.to_dict()),
            'source': source_info.to_dict(),
        },
        'type': 'Feature',
    }


def json_dump(data: dict | list) -> str:
    return json.dumps(data, cls=DefaultJSONEncoder)


def geojson_collection(features: list[dict]) -> dict:
    return {
        'type': 'FeatureCollection',
        'features': features,
    }


def source_results_to_geojson_feature(
    source_info: SourceInfo,
    source_results: dict[str, list[Optional[StaticParkingSiteInput | RealtimeParkingSiteInput]]],
) -> list[dict]:
    output_geojson_features: list[dict] = []
    for static_parking_site_input, realtime_parking_site_input in source_results.values():
        output_geojson_features.append(
            parking_site_inputs_to_geojson_feature(
                source_info=source_info,
                static_parking_site_input=static_parking_site_input,
                realtime_parking_site_input=realtime_parking_site_input,
            ),
        )

    return output_geojson_features


def source_results_to_dict(
    source_info: SourceInfo,
    source_results: dict[str, list[Optional[StaticParkingSiteInput | RealtimeParkingSiteInput]]],
) -> dict[str, dict]:
    return {
        'source': source_info.to_dict(),
        'parking_sites': source_results_to_parking_site_dicts(source_results),
    }


def source_results_to_parking_site_dicts(
    source_results: dict[str, list[Optional[StaticParkingSiteInput | RealtimeParkingSiteInput]]],
) -> list[dict]:
    output_json_items: list[dict] = []
    for static_parking_site_input, realtime_parking_site_input in source_results.values():
        output_json_item = static_parking_site_input.to_dict()

        if realtime_parking_site_input is not None:
            output_json_item.update(realtime_parking_site_input.to_dict())

        output_json_items.append(output_json_item)

    return output_json_items


if __name__ == '__main__':
    main()
