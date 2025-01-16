"""
Giro-e Backend
Copyright (c) 2023, binary butterfly GmbH
All rights reserved.
"""

from typing import List, Optional, Tuple

import pytest
from lxml import etree

from parkapi_sources.util import XMLHelper
from tests.util.data_xml_helper import (
    conditional_remote_type_tags_2a,
    conditional_remote_type_tags_3a,
    ensure_array_keys_1c,
    ignore_attributes_4,
    remote_type_tags_1a,
    remote_type_tags_1b,
    remote_type_tags_2a,
    xml_dict_example_1,
    xml_dict_example_1a,
    xml_dict_example_1b,
    xml_dict_example_1c,
    xml_dict_example_2,
    xml_dict_example_2a,
    xml_dict_example_3,
    xml_dict_example_3a,
    xml_dict_example_4,
    xml_dict_example_5,
    xml_etree_example_1,
    xml_etree_example_2,
    xml_etree_example_3,
    xml_etree_example_4,
    xml_etree_example_5,
)


@pytest.mark.parametrize(
    'input_tag, expected_output, ensure_array_keys, remote_type_tags, conditional_remote_type_tags, ignore_attributes',
    [
        (
            # simple case
            xml_etree_example_1,
            xml_dict_example_1,
            None,
            None,
            None,
            None,
        ),
        (
            # skipping some tags
            xml_etree_example_1,
            xml_dict_example_1a,
            None,
            remote_type_tags_1a,
            None,
            None,
        ),
        (
            # skipping even more tags
            xml_etree_example_1,
            xml_dict_example_1b,
            None,
            remote_type_tags_1b,
            None,
            None,
        ),
        (
            # setting some array keys
            xml_etree_example_1,
            xml_dict_example_1c,
            ensure_array_keys_1c,
            None,
            None,
            None,
        ),
        (
            # other simple example
            xml_etree_example_2,
            xml_dict_example_2,
            None,
            None,
            None,
            None,
        ),
        (
            # using remote type tags to make it even simpler
            xml_etree_example_2,
            xml_dict_example_2a,
            None,
            remote_type_tags_2a,
            None,
            None,
        ),
        (
            # the same but with conditional remote type tags
            xml_etree_example_2,
            xml_dict_example_2a,
            None,
            None,
            conditional_remote_type_tags_2a,
            None,
        ),
        (
            # another simple example with a redundant tag
            xml_etree_example_3,
            xml_dict_example_3,
            None,
            None,
            None,
            None,
        ),
        (
            # removing the redundant tag
            xml_etree_example_3,
            xml_dict_example_3a,
            None,
            None,
            conditional_remote_type_tags_3a,
            None,
        ),
        (
            # solution with ignore_attributes
            xml_etree_example_4,
            xml_dict_example_4,
            None,
            None,
            None,
            ignore_attributes_4,
        ),
        (
            # an attribute and a tag each named 'class',
            # and also a text in combination with children and attributes
            xml_etree_example_5,
            xml_dict_example_5,
            None,
            None,
            None,
            None,
        ),
    ],
)
def test_xml_to_dict(
    input_tag: etree.Element,
    expected_output: dict,
    ensure_array_keys: Optional[List[Tuple[str, str]]],
    remote_type_tags: Optional[List[str]],
    conditional_remote_type_tags: Optional[List[Tuple[str, str]]],
    ignore_attributes: Optional[List[str]],
):
    result_dict: dict = XMLHelper.xml_to_dict(
        tag=input_tag,
        ensure_array_keys=ensure_array_keys,
        remote_type_tags=remote_type_tags,
        conditional_remote_type_tags=conditional_remote_type_tags,
        ignore_attributes=ignore_attributes,
    )

    assert result_dict == expected_output
