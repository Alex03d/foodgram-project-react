import pytest
from rest_framework.test import APIClient

from recipes.models import (Ingredient, Recipe, RecipeIngredient, Subscription,
                            Tag)
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_password():
    return 'strong-test-pass'


@pytest.fixture
def create_user(db, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'username' not in kwargs:
            kwargs['username'] = str(kwargs['email'])
        return User.objects.create_user(**kwargs)
    return make_user


@pytest.fixture
def test_user(create_user):
    user = create_user(email='user@test.com', password='test_password')
    return user


@pytest.fixture
def test_recipe(db, test_user):
    return Recipe.objects.create(
        name='Test recipe',
        text='Test text',
        cooking_time=30,
        author=test_user
    )


@pytest.fixture
def test_ingredient(db):
    return Ingredient.objects.create(
        name='Test ingredient',
        measurement_unit='g'
    )


@pytest.fixture
def test_ingredients(db):
    return [
        Ingredient.objects.create(
            name='Test ingredient 1',
            measurement_unit='g'
        ),
        Ingredient.objects.create(
            name='Test ingredient 2',
            measurement_unit='kg'
        ),
        Ingredient.objects.create(
            name='Another ingredient',
            measurement_unit='ml'
        ),
    ]


@pytest.fixture
def test_tag(db):
    return Tag.objects.create(name='Test tag', color='123456', slug='test')


def test_create_recipe(db, test_user, test_recipe,
                       test_ingredient, test_tag, api_client
                       ):
    api_client.force_authenticate(user=test_user)
    response = api_client.post('/api/recipes/', {
        'name': 'Test recipe',
        'text': 'Test text',
        'cooking_time': 1,
        'ingredients': [{'id': test_ingredient.id, 'amount': 10}],
        'tags': [test_tag.id],
        'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA'
                 'EAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAA'
                 'ACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCB'
                 'yxOyYQAAAABJRU5ErkJggg=='
    }, format='json')
    assert response.status_code == 201


def test_update_recipe(db, test_user, test_recipe, test_ingredient,
                       test_tag, api_client
                       ):
    api_client.force_authenticate(user=test_user)
    response = api_client.patch(f'/api/recipes/{test_recipe.id}/', {
        'name': 'Updated name',
        'text': 'Test text',
        'cooking_time': 1,
        'ingredients': [{'id': test_ingredient.id, 'amount': 10}],
        'tags': [test_tag.id],
        'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAA'
                 'ABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGV'
                 'Kw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
    }, format='json')
    assert response.status_code == 200


def test_delete_recipe(db, test_user, test_recipe, api_client):
    api_client.force_authenticate(user=test_user)
    response = api_client.delete(f'/api/recipes/{test_recipe.id}/')
    assert response.status_code == 204


def test_add_to_shopping_cart(db, test_user, test_recipe, api_client):
    api_client.force_authenticate(user=test_user)
    response = api_client.post(f'/api/recipes/{test_recipe.id}/shopping_cart/')
    assert response.status_code == 201


def test_remove_from_shopping_cart(db, test_user, test_recipe, api_client):
    api_client.force_authenticate(user=test_user)
    api_client.post(f'/api/recipes/{test_recipe.id}/shopping_cart/')
    response = api_client.delete(
        f'/api/recipes/{test_recipe.id}/shopping_cart/'
    )
    assert response.status_code == 204


def test_download_shopping_cart(db, test_user, test_recipe, api_client):
    test_ingredient = Ingredient.objects.create(
        name="Test ingredient",
        measurement_unit="g"
    )
    RecipeIngredient.objects.create(
        recipe=test_recipe,
        ingredient=test_ingredient,
        amount=10
    )

    api_client.force_authenticate(user=test_user)
    response = api_client.post(f'/api/recipes/{test_recipe.id}/shopping_cart/')

    assert response.status_code == 201, 'Adding to shopping cart failed'

    response = api_client.get('/api/recipes/download_shopping_cart/')

    assert response.status_code == 200, 'Downloading shopping cart failed'

    assert 'Test ingredient - 10 g' in str(response.content), \
        'The ingredient list is incorrect'


def test_shopping_list(db, test_user, test_recipe, api_client):
    api_client.force_authenticate(user=test_user)
    api_client.post(f'/api/recipes/{test_recipe.id}/shopping_cart/')
    response = api_client.get('/api/recipes/download_shopping_cart/')
    assert response.status_code == 200


def test_get_ingredients(db, test_ingredients, api_client):
    response = api_client.get('/api/ingredients/')
    assert response.status_code == 200


def test_get_specific_ingredient(db, test_ingredients, api_client):
    ingredient_id = test_ingredients[0].id
    response = api_client.get(f'/api/ingredients/{ingredient_id}/')
    assert response.status_code == 200
    assert response.data['id'] == ingredient_id


def test_get_tags(db, test_tags, api_client):
    response = api_client.get('/api/tags/')
    print(response.data)
    assert response.status_code == 200
    assert all(
        tag.name in (data['name'] for data in response.data)
        for tag in test_tags
    )


@pytest.fixture
def test_subscription(db, test_user, create_user):
    another_user = create_user(
        email='another_user@test.com',
        password='test_password'
    )
    return Subscription.objects.create(user=test_user, author=another_user)


def test_subscribe(db, test_user, test_subscription, api_client):
    api_client.force_authenticate(user=test_user)
    response = api_client.post(
        f'/api/users/{test_subscription.author.id}/subscribe/'
    )
    assert response.status_code == 400  # because already subscribed


def test_unsubscribe(db, test_user, test_subscription, api_client):
    api_client.force_authenticate(user=test_user)
    response = api_client.delete(
        f'/api/users/{test_subscription.author.id}/subscribe/'
    )
    assert response.status_code == 204


def test_subscriptions(db, test_user, test_subscription, api_client):
    api_client.force_authenticate(user=test_user)
    response = api_client.get('/api/users/subscriptions/')
    assert response.status_code == 200
    assert len(response.data['results']) == 1


@pytest.fixture
def test_tags(db):
    return [
        Tag.objects.create(name='Test tag 1', color='123456', slug='test1'),
        Tag.objects.create(name='Test tag 2', color='654321', slug='test2'),
    ]
