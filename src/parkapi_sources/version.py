"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

try:
    # _version.py is generated from the release tag during the package build, see .github/workflows/build-publish.yml
    from parkapi_sources._version import __version__
except ImportError:
    __version__ = 'dev'
