from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from accounts.serializers import UserSerializer
from .models import Recipe, Diet, MediaUpload, Instruction, IngredientName, Ingredient, Comment

def validate_upload_id(value):
    try:
        upload = MediaUpload.objects.get(pk=value)
    except MediaUpload.DoesNotExist:
        raise serializers.ValidationError(f"Media upload with id {value} not found")
    return value

class UploadIDListField(serializers.ListField):
    child = serializers.IntegerField(validators=[validate_upload_id])

class CommentSerializer(serializers.ModelSerializer):

    reply_to = serializers.IntegerField(write_only=True, required=False)
    poster = UserSerializer(read_only=True)
    # Define a custom validator for upload_ids
    upload_ids = UploadIDListField(write_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'poster', 'content', 'last_edited', 'reply_to', 'replies', 'upload_ids', 'uploads']
        depth = 1

    def to_representation(self, instance):
        self.fields['replies'] = CommentSerializer(read_only=True, many=True)
        return super(CommentSerializer, self).to_representation(instance)

    def validate_reply_to(self, value):

        try:
            comment = Comment.objects.get(pk=value)
        except Comment.DoesNotExist:
            raise serializers.ValidationError("Parent comment could not be found")

        return value

    def create(self, validated_data):
        reply_to = validated_data.pop('reply_to', None)

        validated_data['poster'] = self.context['user']
        validated_data['recipe'] = self.context['recipe']
        upload_ids = validated_data.pop('upload_ids')

        if reply_to:
            parent_comment = Comment.objects.get(pk=reply_to)
            validated_data['reply_to']  = parent_comment

        comment = Comment.objects.create(**validated_data)

        if upload_ids:
            for id_ in upload_ids:
                obj = MediaUpload.objects.get(pk=id_)
                comment.uploads.add(obj)

        comment.save()
        return comment

    def update(self, instance, validated_data):

        instance.content = validated_data.get('content', instance.content)
        upload_ids = validated_data.pop('upload_ids')

        if upload_ids:

            removed_objs = list(instance.uploads.exclude(pk__in=upload_ids))
            instance.uploads.clear()
            for removed_obj in removed_objs:
                if len(removed_obj.recipe_set.all()) == 0:
                    removed_obj.delete()

            for id_ in upload_ids:
                obj = MediaUpload.objects.get(pk=id_)
                instance.uploads.add(obj)

        instance.save()
        return instance


class MediaUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = MediaUpload
        fields = ['id', 'upload']

    def create(self, validated_data):
        upload = MediaUpload.objects.create(**validated_data)
        return upload

class InstructionSerializer(serializers.ModelSerializer):

    upload_ids = UploadIDListField(write_only=True)
    uploads = MediaUploadSerializer(read_only=True, many=True)

    class Meta:
        model = Instruction
        fields = ['step', 'instruction', 'upload_ids', 'uploads']


class IngredientNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientName
        fields = ['id', 'name']
        extra_kwargs = {
            "name": {"validators": [UniqueValidator(queryset=IngredientName.objects.all(),
                                                               message="Ingredient with this name already exists.")]}
        }

    def create(self, validated_data):
        obj = IngredientName.objects.create(**validated_data)
        return obj

class IngredientSerializer(serializers.ModelSerializer):

    ingredient_id = serializers.IntegerField(write_only=True)
    ingredient_name = IngredientNameSerializer(read_only=True)
    class Meta:
        model = Ingredient
        fields = ['ingredient_id', 'ingredient_name', 'quantity', 'units']
        depth = 1


class DietSerializer(serializers.ModelSerializer):

    class Meta:
        model = Diet
        exclude = ['id']

class RecipeSerializer(serializers.ModelSerializer):

    creator = UserSerializer(read_only=True)
    diets = DietSerializer(many=True)
    instructions = InstructionSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    upload_ids = UploadIDListField(write_only=True)

    class Meta:
        model = Recipe

        fields = ['id', 'name', 'diets', 'cuisine', 'serving_size', 'prep_time',
                  'ingredients', 'instructions', 'upload_ids', 'uploads', 'creator']
        extra_kwargs = {
            "name" : {"validators" : [UniqueValidator(queryset=Recipe.objects.all(),
                                                      message="Recipe with this name already exists.")]}
        }

        depth = 1

    def validate_ingredients(self, value):
        for ingredient in value:
            print(ingredient.keys())
            try:
                name = IngredientName.objects.get(pk=ingredient['ingredient_id'])
            except IngredientName.DoesNotExist:
                raise serializers.ValidationError(f"Ingredient with id {ingredient['ingredient_id']} does not exist.")

        return value

    def create(self, validated_data):

        diets = validated_data.pop('diets')
        instructions = validated_data.pop('instructions')
        ingredients = validated_data.pop('ingredients')
        upload_ids = validated_data.pop('upload_ids')

        validated_data['creator'] = self.context['user']

        recipe = Recipe.objects.create(**validated_data)
        for diet_data in diets:
            obj = Diet.objects.get_or_create(**diet_data)[0]
            recipe.diets.add(obj)

        for instr_data in instructions:

            instruction_uids = instr_data.pop('upload_ids', None)
            instr = Instruction.objects.create(**instr_data)

            for id_ in instruction_uids:
                upload = MediaUpload.objects.get(pk=id_)
                instr.uploads.add(upload)

            instr.save()
            recipe.instructions.add(instr)

        for ingredient_data in ingredients:
            name = IngredientName.objects.get(pk=ingredient_data['ingredient_id'])
            ingredient = Ingredient.objects.create(ingredient_name=name, quantity=ingredient_data['quantity'],
                                            units=ingredient_data['units'])
            recipe.ingredients.add(ingredient)


        for id_ in upload_ids:
            upload = MediaUpload.objects.get(pk=id_)
            recipe.uploads.add(upload)

        recipe.save()

        return recipe

    def update(self, instance, validated_data):

        diets = validated_data.get('diets')
        instructions = validated_data.get('instructions')
        ingredients = validated_data.get('ingredients')
        upload_ids = validated_data.get('upload_ids')

        if diets != None:
            instance.diets.clear()

            for diet in diets:
                diet = Diet.objects.get_or_create(**diet)[0]
                instance.diets.add(diet)


        if instructions != None:

            instance.instructions.clear()

            for instruction in instructions:
                instruction_uploads = instruction.pop('upload_ids', None)
                instr = Instruction.objects.get_or_create(**instruction)[0]

                if instruction_uploads != None:
                    instr.uploads.clear()
                    for id_ in instruction_uploads:
                        upload = MediaUpload.objects.get(pk=id_)
                        instr.uploads.add(upload)
                instance.instructions.add(instr)


        if ingredients != None:
            instance.ingredients.clear()
            for ingredient_data in ingredients:

                name = IngredientName.objects.get(pk=ingredient_data['ingredient_id'])
                try:
                    ingredient = instance.ingredients.filter(ingredient_name=name)[0]
                    ingredient.quantity = ingredient_data['quantity']
                    ingredient.units = ingredient_data['units']
                    ingredient.save()
                except IndexError:
                    ingredient = Ingredient.objects.create(ingredient_name=name, quantity=ingredient_data['quantity'],
                                              units=ingredient_data['units'])
                instance.ingredients.add(ingredient)

        if upload_ids != None:
            instance.uploads.clear()
            for id_ in upload_ids:
                obj = MediaUpload.objects.get(pk=id_)
                instance.uploads.add(obj)

        instance.name = validated_data.get('name', instance.name)
        instance.cuisine = validated_data.get('cuisine', instance.cuisine)
        instance.serving_size = validated_data.get('serving_size', instance.serving_size)
        instance.prep_time = validated_data.get('prep_time', instance.prep_time)

        instance.save()
        return instance
