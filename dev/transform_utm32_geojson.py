"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import argparse
import json
from pathlib import Path

import pyproj


def main():
    proj: pyproj.Proj = pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True)

    parser = argparse.ArgumentParser(
        prog='ParkAPI-Sources Test Script',
        description='This script helps to develop ParkAPI-Sources converter',
    )
    parser.add_argument('file_path')
    args = parser.parse_args()
    file_path: Path = Path(args.file_path)
    with file_path.open('r') as geojson_file:
        geojson_data = json.loads(geojson_file.read())

    # delete existing crs
    geojson_data.pop('crs', None)

    for feature in geojson_data['features']:
        new_coordinates = []

        # One level
        if feature['geometry']['type'] == 'Point':
            new_lon, new_lat = proj(feature['coordinates'][0], feature['coordinates'][1], inverse=True)
            new_coordinates = [new_lon, new_lat]

        # Two levels
        elif feature['geometry']['type'] in ['LineString', 'MultiPoint']:
            for i in range(len(feature['geometry']['coordinates'])):
                new_coordinates.append([])
                old_lat, old_lon = feature['geometry']['coordinates'][i]
                new_lon, new_lat = proj(old_lat, old_lon, inverse=True)
                new_coordinates[i] = [new_lon, new_lat]

        # Three levels
        elif feature['geometry']['type'] in ['Polygon', 'MultiLineString']:
            for i in range(len(feature['geometry']['coordinates'])):
                new_coordinates.append([])
                for j in range(len(feature['geometry']['coordinates'][i])):
                    new_coordinates[i].append([])
                    old_lat, old_lon = feature['geometry']['coordinates'][i][j]
                    new_lon, new_lat = proj(old_lat, old_lon, inverse=True)
                    new_coordinates[i][j] = [new_lon, new_lat]

        # Four levels
        elif feature['geometry']['type'] in ['MultiPolygon']:
            for i in range(len(feature['geometry']['coordinates'])):
                new_coordinates[i] = []
                for j in range(len(feature['geometry']['coordinates'][i])):
                    new_coordinates[i][j] = []
                    for k in range(len(feature['geometry']['coordinates'][i][j])):
                        new_coordinates[i][j][k] = []
                        old_lat, old_lon = feature['geometry']['coordinates'][i][j][k]
                        new_lon, new_lat = proj(old_lat, old_lon, inverse=True)
                        new_coordinates[i][j][k] = [new_lon, new_lat]

        feature['geometry']['coordinates'] = new_coordinates

    print(json.dumps(geojson_data, indent=2))  # noqa: T201


if __name__ == '__main__':
    main()
