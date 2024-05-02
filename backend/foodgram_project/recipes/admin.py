from django.contrib import admin

from .models import User, Tag, Recipe, Ingredient, Subscription, Amount


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color'
    )
    search_fields = ('name',)


class IngredientsInline(admin.StackedInline):
    model = Amount
    extra = 5


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
    )
    filter_horizontal = ('ingredients',)
    list_filter = (
        'author',
        'name'
    )
    search_fields = ('name',)
    inlines = [IngredientsInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    search_fields = ('user',)


@admin.register(Amount)
class AmountAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredients',
        'amount'
    )
    list_editable = (
        'amount'
    )
