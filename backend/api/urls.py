from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path, include
from . import views
from .views import RecipeViewSet, UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet)
router.register('recipes', views.RecipeViewSet)

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('', include(router.urls)),
]
