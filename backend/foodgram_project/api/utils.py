from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import Amount

CT = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


def shopping_cart(self, request, author):
    sum_of_ingredients = Amount.objects.filter(
        recipe__shop_cart__author=author
    ).values(
        'ingredient__name', 'ingredient__measurment_unit'
    ).annotate(
        amounts=Sum('amount', distinct=True)
    )
    shopping_list = ''
    for ingredient in sum_of_ingredients:
        shopping_list += (
            f'{ingredient["ingredient__name"]} - '
            f'{ingredient["amounts"]} '
            f'{ingredient["ingredient__measurment_unit"]}\n'
        )
    filename = 'shopping_list.docx'
    response = HttpResponse(
        shopping_list,
        content_type=(CT)
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
