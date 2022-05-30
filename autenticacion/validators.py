from django.core.exceptions import ValidationError
import re

class ValidateAlphanumericPassword:
    """
    Validate that the password is alphanumeric.
    """

    def validate(self, password, user=None):
        pat = re.compile(r"^(\w+\d+|\d+\w+)+$")

        if not re.fullmatch(pat, password):
            raise ValidationError(
                "La contraseña debe ser una combinación de letras y números.",
                code="password_not_alphanumeric",
            )

    def get_help_text(self):
        return 'Su contraseña debe ser una combinación de letras y números.'