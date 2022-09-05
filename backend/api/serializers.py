from api.models import (Cart, Favorite, Ingredient, IngredientAmount, Recipe,
                        Tag)
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from foodgram.settings import LEAST_AMOUNT_INGREDIENT, MINIMUM_COOKING_TIME
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        validators = (
            UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('name', 'measurement_unit')
            ),
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = (
            UniqueTogetherValidator(
                queryset=IngredientAmount.objects.all(),
                fields=('ingridients', 'recipe')
            ),
        )


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'is_favorited',
            'is_in_shopping_cart',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exists()

    def validate(self, data):
        ingredients = data.get('ingredientamount_set')
        cooking_time = data.get('cooking_time')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'нет ингредиентов'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_item.get('id'))
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиент уже добавлен'}
                )
            ingredient_list.append(ingredient)
            if int(ingredient_item.get('amount')) <= LEAST_AMOUNT_INGREDIENT:
                raise serializers.ValidationError(
                    {'ingredients': 'количества слишком мало '}
                )
        if cooking_time < MINIMUM_COOKING_TIME:
            raise serializers.ValidationError(
                {'cooking_time': 'время слишком мало '}
            )
        return data

    def create_ingredients(self, ingredients, recipe):
        objs = []
        for ingredient in ingredients:

            ing = get_object_or_404(Ingredient, id=ingredient.get('id'))
            obj = IngredientAmount(
                recipe=recipe,
                ingredient=ing,
                amount=ingredient.get('amount')
            )
            objs.append(obj)
        IngredientAmount.objects.bulk_create(objs)

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredientamount_set')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredientamount_set')
        super().update(instance, validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags_data)
        instance.recipe.ingridients.delete()
        self.create_ingredients(ingredients_data, instance)
        return instance


class RecipeSerializerRead(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'is_favorited',
            'is_in_shopping_cart',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exists()


class CropRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    class Meta:
        model = Follow
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            ),
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.author.recipies.all()
        if limit:
            queryset = queryset[: int(limit)]
        return CropRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipies.count()

    def validate(self, data):
        author = self.initial_data.get('author')
        user = self.context.get('request').user
        if author == user:
            raise serializers.ValidationError(
                {'errors': 'Вы не можете отписываться от самого себя'}
            )


class FavoriteSerializer(serializers.ModelSerializer):
    validators = (
        UniqueTogetherValidator(
            queryset=Favorite.objects.all(),
            fields=('user', 'recipe')
        ),
    )


class CartSerializer(serializers.ModelSerializer):
    validators = (
        UniqueTogetherValidator(
            queryset=Cart.objects.all(),
            fields=('user', 'recipe')
        ),
    )


class UnfollowSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if not Follow.objects.filter(
            author=data.get('author'),
            user=data.get('user')
        ).exists():
            raise serializers.ValidationError(
                {'author': 'Автор не в подписках.'}
            )
        return data
