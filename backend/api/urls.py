from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
urlpatterns = router.urls
