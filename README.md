# ParkAPI Sources

ParkAPI Sources is a collection of converters from several different data sources to normalized ParkAPI data. ParkAPI does support parking
for cars, for bikes and lockers. The data model is based on the original ParkAPI project and tries to stay compatible to DATEX II Parking
Publication Light at any extension of the model.

We support following data sources:

| name                                                           | purpose    | type        | uid                      | realtime |
|----------------------------------------------------------------|------------|-------------|--------------------------|----------|
| Aachen                                                         | car        | pull        | `aachen`                 | yes      |
| APCOA Services                                                 | car        | pull        | `apcoa`                  | no       |
| Deutsche Bahn                                                  | car & bike | pull        | `bahn_v2`                | no       |
| Stadt Bietigheim-Bissingen                                     | car        | pull        | `bietigheim_bissingen`   | yes      |
| Barrierefreie Reisekette Baden-Württemberg: PKW-Parkplätze     | car        | pull        | `bfrk_bw_car`            | no       |
| Barrierefreie Reisekette Baden-Württemberg: Fahrrad-Parkplätze | bike       | pull        | `bfrk_bw_bike`           | no       |
| Stadt Ellwangen                                                | car        | push (xlsx) | `ellwangen`              | no       |
| Stadt Buchen                                                   | car        | push (json) | `buchen`                 | yes      |
| Stadt Freiburg                                                 | car        | pull        | `freiburg`               | yes      |
| GOLDBECK Parking Services                                      | car        | push (xlsx) | `goldbeck`               | no       |
| Stadt Heidelberg                                               | car        | pull        | `heidelberg`             | yes      |
| Stadt Herrenberg                                               | car        | pull        | `herrenberg`             | no       |
| Stadt Herrenberg - Munigrid                                    | bike       | pull        | `herrenberg_bike`        | no       |
| PARK SERVICE HÜFNER GmbH + Co. KG                              | car        | push (xlsx) | `huefner`                | no       |
| Stadt Karlsruhe: PKW-Parkplätze                                | car        | pull        | `karlsruhe`              | yes      |
| Stadt Karlsruhe: Fahhrrad-Abstellangen                         | bike       | pull        | `karlsruhe_bike`         | no       |
| Kienzler: Bike and Ride                                        | bike       | pull        | `kienzler_bike_and_ride` | yes      |
| Kienzler: Karlsruhe                                            | bike       | pull        | `kienzler_karlruhe`      | yes      |
| Kienzler: Neckarsulm                                           | bike       | pull        | `kienzler_neckarsulm`    | yes      |
| Kienzler: Offenburg                                            | bike       | pull        | `kienzler_offenburg`     | yes      |
| Kienzler: RadSafe                                              | bike       | pull        | `kienzler_rad_safe`      | yes      |
| Kienzler: Stuttgart                                            | bike       | pull        | `kienzler_stuttgart`     | yes      |
| Kienzler: VRN                                                  | bike       | pull        | `kienzler_vrn`           | yes      |
| Konstanz                                                       | car        | pull        | `konstanz`               | yes      |
| Stadt Konstanz: Fahrrad-Abstellanlagen                         | bike       | push        | `konstanz_bike`          | no       |
| Stadt Mannheim                                                 | car        | push (json) | `mannheim`               | yes      |
| Stadt Neckarsulm: PKW-Parkplätze                               | car        | pull        | `neckarsulm`             | no       |
| Stadt Neckarsulm: Fahrrad-Abstellanlagen                       | bike       | pull        | `neckarsulm_bike`        | no       |
| Open-Data-Plattform öV Schweiz                                 | car        | pull (json) | `opendata_swiss`         | no       |
| P + M Baden-Württemberg                                        | car        | pull        | `p_m_bw`                 | yes      |
| Baden-Württemberg: Parken und Mitfahren                        | car        | push (xlsx) | `pum_bw`                 | no       |
| RadVIS Baden-Württemberg (experimental)                        | bike       | pull        | `radvis_bw`              | no       |
| Parkraumgesellschaft Baden-Württemberg                         | car        | pull        | `pbw`                    | yes      |
| Stadt Pforzheim                                                | car        | push (csv)  | `pforzheim`              | no       |
| Stadt Reutlingen: PKW-Parkplätze                               | car        | push (csv)  | `reutlingen`             | no       |
| Stadt Reutlingen: Fahrrad-Abstellanlagen                       | bike       | push (csv)  | `reutlingen_bike`        | no       |
| Stadt Stuttgart                                                | car        | push (json) | `stuttgart`              | yes      |
| Stadt Ulm                                                      | car        | pull        | `ulm`                    | yes      |
| Velobrix                                                       | bike       | pull        | `velobrix`               | yes      |
| Verkehrsverbund Rhein-Neckar GmbH: P+R Parkplätze              | car        | pull        | `vrn_p_r`                | yes      |
| Verband Region Stuttgart: Bondorf                              | car        | pull        | `vrs_bondorf`            | yes      |
| Verband Region Stuttgart: Kirchheim                            | car        | pull        | `vrs_kirchheim`          | yes      |
| Verband Region Stuttgart: Neustadt                             | car        | pull        | `vrs_neustadt`           | yes      |
| Verband Region Stuttgart: Park and Ride                        | car        | push (xlsx) | `vrs_p_r`                | no       |
| Verband Region Stuttgart: Vaihingen                            | car        | pull        | `vrs_vaihingen`          | yes      |

New converters for new sources are always welcome, please have a look at "Contribute" below.


## Install

ParkAPI Sources is a python module published at [PyPI](https://pypi.org/project/parkapi-sources/). Therefore, you can install it by

```shell
pip install parkapi-sources
```

If you use parkapi-sources in a project, we recommend to fix the version. As long as parkapi-sources is beta, breaking changes might be
introduced on minor version level (like: change from 0.1.1 to 0.2.0). As soon as 1.0 is released, we will follow
[Semantic Versioning](https://semver.org), which means that breaking changes will just appear on major version changes (like: change from 1.1.2 to 2.0.0).
You can expect a lot of changes in the minor version level, as any new converter is a new feature.


## Usage

Your starting point is always the `ParkAPISources` where all Sources are registered.

```python
from parkapi_sources import ParkAPISources

my_sources = ParkAPISources()
```

`ParkAPISources` accepts following parameters:

- `config: Optional[dict] = None` is a dictionary for config values, especially secrets.
- `converter_uids: Optional[list[str]] = None` is used for loading just the converter uids you want to load
- `no_pull_converter: bool = False` is used for limiting converters to pull converters
- `no_push_converter: bool = False` is used for limiting converters to push converters


### Configuration

Config values are mostly individual for specific converters: if there are required config values, they are defined at the converter
definition right at the top:

```
required_config_keys = ['MY_SECRET']
```

`ParkAPISources` offers a method to check if all config values are set:

```python
from parkapi_sources import ParkAPISources

my_sources = ParkAPISources()
my_sources.check_credentials()
```

If not all config values are set, a `MissingConfigException` is thrown. It's recommended to run this check after initializing the module
to prevent exceptions during runtime.

Besides converter-individual config values, there are two global values which can be used to configure the source of GeoJSON files. Per
default, static GeoJSON files are fetched from this repository. This behaviour can be changed:

- `STATIC_GEOJSON_BASE_URL` defines another base URL for GeoJSON files
- `STATIC_GEOJSON_BASE_PATH` defines a lokal path instead, so the application will load files locally without network requests


### Use converters

After initializing, you will find all initialized converters at `ParkAPISources.converter_by_uid`. As the input is very different, so are
the methods you have to use. In general, you can differ between two major strategies:


### Pull converters

Pull converters are responsible for getting data from an external data source. This can be an REST endpoints as well as HTML which is
scraped. Pull converters always split up in static and realtime data, because at most sources, this is not the same. Each pull converter
has two methods:

1) `get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:`
2) `def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:`


### Push converters

Push converters are responsible to handle data which is pushed to the service using defined endpoints. Usually, these converters are used
as a handler behind HTTP endpoints, but of course you can use them in other ways, too, for example command line scripts.

Push converters always handle specific formats, therefore, there are multiple types of push converters. All push converters return a
`tuple[list[StaticParkingSiteInput | RealtimeParkingSiteInput], list[ImportParkingSiteException]]`, therefore they decided based on the
given data if it's static or realtime data they got - or even both, then each dataset ends up in two entries in the first list.

1) A `CsvConverter` handles CSV files: `handle_csv_string(self, data: StringIO)`
2) A `JsonConverter` handles JSON based data: `handle_json(self, data: dict | list)`
3) A `XlsxConverter` handles XMLX data: `def handle_xlsx(self, workbook: Workbook)` parsed by `openpyxl`
4) A `XmlConverter` handles XML data: `def handle_xml(self, root: Element)` parsed by `lxml`


### Results

At `webapp/models/parking_site_inputs.py`, you can find the definition of `StaticParkingSiteInput` and `RealtimeParkingSiteInput`. These
`dataclasses` are also [`validataclasses`](https://pypi.org/project/validataclass/), so you can be sure that the data you get is validated.


### Debugging

In order to debug ParkAPI Sources, there are two config values which can be used to dump all the requests. Before doing
this, please keep in mind that this might end into a lot of data on your disk, especially in case of realtime enabled
sources. Please also keep in mind that dumps will contain credentials in case of sources with credentials, so please
handle this data the same way as you handle passwords.

Two config values are required for enabling debugging:

- `DEBUG_SOURCES` should be a list of source uids which should be debugged
- `DEBUG_DUMP_DIR` is the directory where the requests get dumped to

Setting these two values will make ParkAPI Sources save all requests in
`{DEBUG_DUMP_DIR}/{source_uid}/{datetime}-{type}`, with type:

- `metadata`: Metadata like url, http method, http status, request and response headers and request body
- `response-body`: The response body

With this data, you can start a deeper analysis why things don't work as expected.


## Contribute

We are happy about any contributions. We do not expect that yoy can develop Python, but of course things might speed up if


### Report bugs

As ParkAPI-Sources integrates a lot of external data sources, sometimes without a proper definition, converters might run into issues
because of changes on the data source side. If you see that happening, please add a bug report at the
[issues](https://github.com/ParkenDD/parkapi-sources-v3/issues). If possible, please add the data which fails.


### Contribute new source data

If you see a nice data source which is not covered by ParkAPI-sources, you can always create a feature request at our
[issues](https://github.com/ParkenDD/parkapi-sources-v3/issues). If you do so, please add the data you found, so we can actually build
the converter. If possible, please try to find out a licence, too.


### Write a new Converters

We always welcome merge requests with new converters. A merge request should contain the following:

* MIT licenced code
* A converter which validates the input in a way that the output follows the data model
* A test with example data to ensure that the converter works with current data


## Write a new converter

First you have to determine which type of converter you need. If you get the data from an endpoint, you will need a `PushConverter`, if
you have a file you want to push via HTTP or CLI, you need a `PullConverter`.


### Write the converter

In order to write a converter, you need a directory at `converters`. Please name your directory in a way that it points to the actual
converter you will write. If it's just one converter, the `uid` is usually the best approach.

At `converters/your-converter`, you will at least need a `converter.py` and an `__init__.py`. In most cases, you will also need some
`validataclasses` you can put in `models.py`. Validation is crucial in this library, because the users of this library should not think
invalid data. Additionally, if you have very specific new data types, you can write new `validataclass` validators you can usually put in
`validators.py`.


### Testing the converter

In order to proof that the validator works, we need to test the basic functionality. In order to do this, we need a snapshot of the data
which should be integrated. Common place for this data is `tests/converters/data/filename-starting-with-uid.ending`. This data should be
used in one or multiple tests (in several cases two tests, one for static, one for realtime data) stored at `tests/converters/uid_test.py`.

If you test a `PullConverter`, you will need no mock requests. This can be done using the fantastic
[`requests_mock`](https://pypi.org/project/requests-mock/) library.

If you created new validators, these should be tested with different inputs. Usually, `pytest.parametrize` is a nice approach to do this.


### Migrate a converter

If you want to migrate a v1 or v2 converter, you can re-use some of the code. There is a paradigm change, though: `parkapi-source-v3`
enforces a strict validation after transforming the data, while v1 and v2 converters don't. ParkAPI v1 / v2 converters are always pull
converters, so the base class is always `PullConverter`.

Instead of defining `POOL`, you will set `source_info` at the same place. Attributes are almost the same, except for `id` was renamed to
`uid`, and there is the new attribute `has_realtime_data`, which has to be set.

ParkAPI v1 and v2 used two methods for static and realtime data, just as `parkapi-sources-v3`:

- the old static data handling `def get_lot_infos(self) -> List[LotInfo]:` is
  `get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:` in `parkapi-sources-v3`.
- the old realtime data handling`def get_lot_data(self) -> List[LotData]:` is
  `def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:` in
  `parkapi-sources-v3`.

The result objects have quite the same idea, too:

- `LotInfo` gets `StaticParkingSiteInput`
- `LotData` gets `RealtimeParkingSiteInput`

There's also a helper for scraped content: before, there was `self.request_soup(self.POOL.public_url)` in order to get a `BeautifulSoup`
element. Now, there is a helper mixin called `PullScraperMixin`. You can use it this way:

```
class MyPullConverter(PullConverter, PullScraperMixin):
```

Additionally, there is another mixin for the GeoJSON files you already know from v1 and v2 converters: `StaticGeojsonDataMixin`. Using this,
you can just define the static data method this way:

```
    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_static_parking_site_inputs_and_exceptions(source_uid=self.source_info.uid)
```

The default location for GeoJSON files is a [separate repository](https://github.com/ParkenDD/parkapi-static-data).

Please keep in mind that you will have to add tests for the migrated scraper.


### Linting

As we try to keep a consistent code style, please lint your code before creating the merge request. We use `ruff` for linting and
formatting. There is Makefile target to do both: `make lint`. It runs the following commands:

```bash
ruff format ./src ./tests
ruff check --fix ./src ./tests
```

If you don't have `ruff` installed globally, you can create a virtual environment for these tools:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

ruff format ./src ./tests
ruff check --fix ./src ./tests
```


### Make your new converter available

All available converters should be registered at the `ParkAPISources` class in order to make them accessible for users of this library, so
please register your converter there. The new converter should also be added to the table in this README.md file.


### Release process

If you created a merge request, the maintainers will review your code. If everything is fine, it will be merged to `main`, and a new
release will be created soon. As written above, we follow SemVer, so any new converter will add plus one to the minor version. In order to
use this new release, please keep in mind to update your `requirements.txt` / update the dependency manager you use.


## Licence

This library is under MIT licence. Please look at `LICENCE.txt` for details.
