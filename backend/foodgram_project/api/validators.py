import re

from django.core.exceptions import ValidationError

pattern = r'[\w.@+-]'


def validate_username(username):
    if username == 'me':
        raise ValidationError(
            f'Имя пользователя {username} запрещено.'
        )
    forbidden_symbols = re.sub(pattern, '', username)
    if forbidden_symbols:
        forbidden_symbols = ''.join(set(forbidden_symbols))
        raise ValidationError(
            f'Нельзя использовать символы: {forbidden_symbols}'
        )

    return username
