from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AuthToken, CustomUserViewSet,
    IngredientViewSet,
    RecipeViewSet, TagViewSet,
)


router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path(
        'auth/',
        include(
            [
                path('', include('djoser.urls.authtoken')),
                path('token/login/', AuthToken.as_view(), name='login')
            ]
        ),
    )

]
