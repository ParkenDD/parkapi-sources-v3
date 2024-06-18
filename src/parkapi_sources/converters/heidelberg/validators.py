"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Optional

from validataclass.validators import Validator


class RemoveValueDict(Validator):
    wrapped_validator: Validator

    def __init__(self, validator: Validator):
        # Check parameter validity
        if not isinstance(validator, Validator):
            raise TypeError('RemoveValueDict requires a Validator instance.')

        self.wrapped_validator = validator

    def validate(self, input_data: Any, **kwargs: Any) -> Any:
        self._ensure_type(input_data, dict)

        return self.wrapped_validator.validate(input_data.get('value'), **kwargs)


class NoneableRemoveValueDict(RemoveValueDict):
    def validate(self, input_data: Any, **kwargs: Any) -> Optional[Any]:
        if input_data is None:
            return None

        return super().validate(input_data, **kwargs)
