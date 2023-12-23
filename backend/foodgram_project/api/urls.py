from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, TagViewSet,
                    IngredientViewSet, RecipeViewSet, UserFollowViewSet)

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/subscriptions/', UserFollowViewSet.as_view({'get': 'list'})),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
