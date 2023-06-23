from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, ShoppingListManipulation, TagViewSet


app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'users', UserViewSet, basename='user')
router.register(r'tags', TagViewSet, basename='tag')


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('recipes/<int:id>/shopping_cart/', ShoppingListManipulation.as_view()),
]
