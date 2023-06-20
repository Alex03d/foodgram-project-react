from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import RecipeViewSet
from djoser.views import UserViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'users', UserViewSet, basename='user')

# urlpatterns = router.urls + [
#     path('auth/', include('djoser.urls')),
#     path('auth/token/login/', obtain_auth_token, name='token_obtain'),  # изменено
# ]

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]

# from django.urls import include, path
# from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
# from .views import RecipeViewSet
# from djoser.views import UserViewSet
#
# app_name = 'api'
#
# router = DefaultRouter()
# router.register(r'recipes', RecipeViewSet, basename='recipe')
# router.register(r'users', UserViewSet, basename='user')
#
# urlpatterns = router.urls + [
#     path('auth/', include('djoser.urls')),
#     path('auth/token/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]

