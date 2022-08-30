from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientFilter, TagAuthorFilter
from api.models import (Cart, Favorite, Ingredient, IngredientAmount, Recipe,
                        Tag)
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (CropRecipeSerializer, IngredientSerializer,
                             RecipeSerializer, RecipeSerializerRead,
                             TagSerializer)
from foodgram.settings import FILENAME


CONTENT_TYPE = 'Content-Type: text/plain'


class TagViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngrViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientFilter,)
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_class = TagAuthorFilter
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializerRead
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_object(Cart, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_object(Cart, request.user, pk)
        return None

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_for_shoping(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__cart__user=request.user
        ).values(
            ingredient_n=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).annotate(amount_sum=Sum('amount'))

        shop_list = '      Список покупок\n'

        for n, (ing) in enumerate(ingredients, 1):
            shop_list += (
                f'{n}. {ing["ingredient_n"]} -'
                + f'{ing["amount_sum"]} {ing["unit"]}\n'
            )
        response = HttpResponse(
            shop_list, content_type=CONTENT_TYPE
        )

        response['Content-Disposition'] = FILENAME
        return response

    def delete_object(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт уже был удален'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def add_object(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Рецепт уже был добавлен'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = CropRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == 'DELETE':
            return self.delete_object(Favorite, request.user, pk)

        elif request.method == 'POST':
            return self.add_object(Favorite, request.user, pk)

        return None
