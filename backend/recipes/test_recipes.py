import pytest
from rest_framework.test import APIClient
from users.models import User
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from api.serializers import RecipeSerializer


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
def test_tag(db):
    return Tag.objects.create(name='Test tag', color='123456', slug='test')


def test_create_recipe(db, test_user, test_recipe, test_ingredient, test_tag, api_client):
    api_client.force_authenticate(user=test_user)
    response = api_client.post('/api/recipes/', {
        'name': 'Test recipe',
        'text': 'Test text',
        'cooking_time': 1,
        'ingredients': [{'id': test_ingredient.id, 'amount': 10}],
        'tags': [test_tag.id],
        'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
    }, format='json')
    assert response.status_code == 201


def test_update_recipe(db, test_user, test_recipe, test_ingredient, test_tag, api_client):
    api_client.force_authenticate(user=test_user)
    response = api_client.patch(f'/api/recipes/{test_recipe.id}/', {
        'name': 'Updated name',
        'text': 'Test text',
        'cooking_time': 1,
        'ingredients': [{'id': test_ingredient.id, 'amount': 10}],
        'tags': [test_tag.id],
        'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
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
    # сначала добавим рецепт в список покупок
    api_client.force_authenticate(user=test_user)
    api_client.post(f'/api/recipes/{test_recipe.id}/shopping_cart/')
    # теперь удалим его
    response = api_client.delete(f'/api/recipes/{test_recipe.id}/shopping_cart/')
    assert response.status_code == 204


def test_download_shopping_cart(db, test_user, test_recipe, api_client):
    # Добавляем ингредиент в рецепт при его создании
    test_ingredient = Ingredient.objects.create(name="Test ingredient", measurement_unit="g")
    RecipeIngredient.objects.create(recipe=test_recipe, ingredient=test_ingredient, amount=10)

    # Сначала добавляем рецепт в список покупок
    api_client.force_authenticate(user=test_user)
    response = api_client.post(f'/api/recipes/{test_recipe.id}/shopping_cart/')

    # Проверяем, успешно ли был добавлен рецепт
    assert response.status_code == 201, 'Adding to shopping cart failed'

    # Теперь скачиваем список
    response = api_client.get('/api/recipes/download_shopping_cart/')

    assert response.status_code == 200, 'Downloading shopping cart failed'

    # Проверяем содержимое файла, которое может зависеть от вашей реализации
    assert 'Test ingredient - 10 g' in str(response.content), 'The ingredient list is incorrect'
