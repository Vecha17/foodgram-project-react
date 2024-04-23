from .validators import validate_username


class ValidateUsernameMixin:

    @staticmethod
    def validate_username(username):
        return validate_username(username)
