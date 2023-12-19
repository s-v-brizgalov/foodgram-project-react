from django.shortcuts import get_object_or_404
from product.models import Recipe, User
from rest_framework import status
from rest_framework.response import Response

from .serializer import RecipeminSerializer


def add_delete_fun(request, pk, model):
    recipe = get_object_or_404(Recipe, id=pk)
    user = get_object_or_404(User, username=request.user)
    if request.method == 'POST':
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeminSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    instance = model.objects.filter(user=user, recipe=recipe)
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
