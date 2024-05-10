# Foodgram

Foodgram - это интернет-сервис для публикации рецептов. Пользователи могут добавлять свои рецепты, подписываться на других пользователей, добавлять понравившиеся рецепты в в список "избранное", а также скачать список продуктов, необходимых для приготовления конкретного рецепта.

# Примеры запросов

Получание списка пользователей
GET http://127.0.0.1:8000/api/users/

```
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "email": "test@test.com",
            "id": 1,
            "username": "Admin",
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "is_subscribed": false
        },
        {
            "email": "test2@test.com",
            "id": 2,
            "username": "Bobik",
            "first_name": "Bob",
            "last_name": "Smith",
            "is_subscribed": true
        },
        {
            "email": "second_user@email.org",
            "id": 4,
            "username": "second-user",
            "first_name": "Андрей",
            "last_name": "Макаревский",
            "is_subscribed": false
        },
        {
            "email": "third-user@user.ru",
            "id": 5,
            "username": "third-user-username",
            "first_name": "Гордон",
            "last_name": "Рамзиков",
            "is_subscribed": false
        },
        {
            "email": "vpupkin@yandex.ru",
            "id": 3,
            "username": "vasya.pupkin",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "is_subscribed": false
        }
    ]
}
```

Получание списка рецептов

GET http://127.0.0.1:8000/api/recipes

```
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 3,
            "tags": [],
            "author": {
                "email": "second_user@email.org",
                "id": 4,
                "username": "second-user",
                "first_name": "Андрей",
                "last_name": "Макаревский",
                "is_subscribed": false
            },
            "ingredients": [],
            "is_favorite": false,
            "is_in_shopping_cart": false,
            "name": "Нечто съедобное (это не точно)",
            "image": "http://127.0.0.1:8000/static/images/temp_Cs6kb6E.png",
            "text": "Приготовьте как нибудь эти ингредиеты",
            "cooking_time": 5
        },
        {
            "id": 2,
            "tags": [],
            "author": {
                "email": "test@test.com",
                "id": 1,
                "username": "Admin",
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "is_subscribed": false
            },
            "ingredients": [],
            "is_favorite": true,
            "is_in_shopping_cart": false,
            "name": "Тест1",
            "image": "http://127.0.0.1:8000/static/images/temp.png",
            "text": "123",
            "cooking_time": 123
        },
        {
            "id": 1,
            "tags": [
                {
                    "id": 1,
                    "name": "Завтрак",
                    "color": "#7CFC00",
                    "slug": "zavtrak"
                }
            ],
            "author": {
                "email": "test2@test.com",
                "id": 2,
                "username": "Bobik",
                "first_name": "Bob",
                "last_name": "Smith",
                "is_subscribed": true
            },
            "ingredients": [
                {
                    "id": 5,
                    "name": "абрикосы",
                    "measurement_unit": "г",
                    "amount": 1
                }
            ],
            "is_favorite": true,
            "is_in_shopping_cart": false,
            "name": "тестовый завтарк",
            "image": "http://127.0.0.1:8000/Aga.jpg",
            "text": "Ага",
            "cooking_time": 10
        }
    ]
}
```