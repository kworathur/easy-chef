from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Recipe, Instruction, Ingredient

@receiver(post_delete, sender=Recipe)
def cleanup_recipe_details(sender, **kwargs):

    # Delete any instructions, ingredients which do not belong to a recipe
    for instruction in Instruction.objects.all():
        if (len(instruction.recipe_set.all()) == 0):
            instruction.delete()

    for ingredient in Ingredient.objects.all():
        if len(ingredient.recipe_set.all()) == 0:
            ingredient.delete()

    return None