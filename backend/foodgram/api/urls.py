from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSets, RecipeViewSets, TagsViewSets,
                    UserViewSets, SubscriptionsViewSets)

router = DefaultRouter()

router.register('ingredients', IngredientsViewSets)
router.register('tags', TagsViewSets)
router.register('recipes', RecipeViewSets)
router.register(
    r'users/subscriptions',
    SubscriptionsViewSets,
    basename='subscriptions'
)
router.register('users', UserViewSets)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
