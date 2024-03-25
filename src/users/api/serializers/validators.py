import re

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from rest_framework import serializers


class AggregatedValidator:
    _validators = []

    def __call__(self, value):
        for validator in self._validators:
            validator(value)


class BaseCheckValidator:
    message = None
    code = None

    def __call__(self, value):
        if not self._check(value):
            raise DjangoValidationError(self.message, code=self.code)

    def _check(self, value):
        raise NotImplementedError


class PasswordValidator(AggregatedValidator):
    class OneDigitValidator(BaseCheckValidator):
        message = "Ensure this value contains one digit."
        code = "capital_letter"

        def _check(self, value):
            return bool(re.search(r"[0-9]", value))

    class CapitalLetterValidator(BaseCheckValidator):
        message = "Ensure this value contains one capital letter."
        code = "capital_letter"

        def _check(self, value):
            return bool(re.search(r"[A-Z]", value))

    class SpecialSymbolValidator(BaseCheckValidator):
        message = "Ensure this value contains one special symbol."
        code = "special_symbol"

        def _check(self, value):
            return bool(re.search(r"[!@#$%^&*()\-_=+\[{\]}|;:\'\",<.>/?]", value))

    _validators = [
        MinLengthValidator(limit_value=8, message="Ensure this value has at least %(limit_value)d characters."),
        MaxLengthValidator(limit_value=128, message="Ensure this value has at most %(limit_value)d characters."),
        OneDigitValidator(),
        CapitalLetterValidator(),
        SpecialSymbolValidator()
    ]


class PasswordEqualValidator:
    requires_context = False

    def __call__(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password2": "Password invalid."
            })
