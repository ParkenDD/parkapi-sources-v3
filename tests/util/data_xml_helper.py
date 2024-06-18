"""
Giro-e Backend
Copyright (c) 2023, binary butterfly GmbH
All rights reserved.
"""

from typing import List, Tuple

from lxml import etree

xml_string_example_1: str = """
            <Envelope>
                <Header>
                    <Security>
                        <UsernameToken>
                            <Username>Ghost</Username>
                            <Password>Boo</Password>
                        </UsernameToken>
                    </Security>
                </Header>
                <Body>
                    <Content>
                        <ContentText>
                            <Text>some text</Text>
                        </ContentText>
                    </Content>
                </Body>
            </Envelope>
"""

xml_etree_example_1: etree.Element = etree.fromstring(xml_string_example_1)  # noqa: S320

xml_dict_example_1: dict = {
    'Envelope': {
        'Body': {
            'Content': {
                'ContentText': {
                    'Text': 'some text',
                }
            }
        },
        'Header': {
            'Security': {
                'UsernameToken': {
                    'Password': 'Boo',
                    'Username': 'Ghost',
                }
            }
        },
    }
}

remote_type_tags_1a: List[str] = ['Content', 'ContentText', 'Text', 'Security', 'UsernameToken']

xml_dict_example_1a: dict = {
    'Envelope': {
        'Body': 'some text',
        'Header': {
            'Password': 'Boo',
            'Username': 'Ghost',
        },
    }
}

remote_type_tags_1b: List[str] = ['Envelope', 'Content', 'ContentText', 'Text', 'Security', 'UsernameToken']

xml_dict_example_1b: dict = {
    'Body': 'some text',
    'Header': {
        'Password': 'Boo',
        'Username': 'Ghost',
    },
}

ensure_array_keys_1c: List[Tuple[str, str]] = [('Envelope', 'Header'), ('Content', 'ContentText')]

xml_dict_example_1c: dict = {
    'Envelope': {
        'Body': {
            'Content': {
                'ContentText': [
                    {'Text': 'some text'},
                ]
            }
        },
        'Header': [
            {'Security': {'UsernameToken': {'Password': 'Boo', 'Username': 'Ghost'}}},
        ],
    }
}


xml_string_example_2: str = """
            <status>
                <ChargePointStatusType>Operative</ChargePointStatusType>
            </status>
"""

xml_etree_example_2: etree.Element = etree.fromstring(xml_string_example_2)  # noqa: S320

xml_dict_example_2: dict = {
    'status': {
        'ChargePointStatusType': 'Operative',
    }
}

remote_type_tags_2a: List[str] = ['ChargePointStatusType']

conditional_remote_type_tags_2a: List[Tuple[str, str]] = [('status', 'ChargePointStatusType')]

xml_dict_example_2a: dict = {
    'status': 'Operative',
}

xml_string_example_3: str = """
        <resultCode>
            <resultCode>ok</resultCode>
        </resultCode>
"""

xml_etree_example_3: etree.Element = etree.fromstring(xml_string_example_3)  # noqa: S320

xml_dict_example_3: dict = {
    'resultCode': {
        'resultCode': 'ok',
    }
}

conditional_remote_type_tags_3a: List[Tuple[str, str]] = [('resultCode', 'resultCode')]

xml_dict_example_3a: dict = {
    'resultCode': 'ok',
}

xml_string_example_4: str = """
    <resultDescription xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
"""

xml_etree_example_4: etree.Element = etree.fromstring(xml_string_example_4)  # noqa: S320

ignore_attributes_4: List[str] = ['{http://www.w3.org/2001/XMLSchema-instance}nil']

xml_dict_example_4: dict = {
    'resultDescription': None,
}

xml_string_example_5: str = """
        <topLevelTag class="testClass">
            testText
            <secondLevelTag>ok</secondLevelTag>
            <class>anotherTestClass</class>
        </topLevelTag>
"""

xml_etree_example_5: etree.Element = etree.fromstring(xml_string_example_5)  # noqa: S320

xml_dict_example_5: dict = {
    'topLevelTag': {
        '_text': 'testText',
        'class': 'testClass',
        'class_': 'anotherTestClass',
        'secondLevelTag': 'ok',
    }
}
