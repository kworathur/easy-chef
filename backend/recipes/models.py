from django.db import models
from accounts.models import User
from django.core.validators import MinValueValidator, FileExtensionValidator

# Create your models here.
class MediaUpload(models.Model):
    objects = models.Manager()

    upload = models.FileField(unique=True, upload_to="recipe_media/",
                             validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'mp4'])])

    def __str__(self):
        return str(self.upload)

class Diet(models.Model):
    objects = models.Manager()

    diet = models.CharField(max_length=30)

    def __str__(self):
        return "Diet: {}".format(self.diet)

class IngredientName(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=100)

    def __str__(self):
        return "{}".format(self.name)

class Ingredient(models.Model):

    objects = models.Manager()
    ingredient_name = models.ForeignKey(to=IngredientName, on_delete=models.CASCADE)

    quantity = models.DecimalField(default=0.0, max_digits=5, decimal_places=2)
    CUPS = 'cups'
    GRAMS = 'grams'
    TABLESPOONS = 'tbsp'
    UNITS_CHOICES = [
        (CUPS, 'Cups'),
        (GRAMS, 'Grams'),
        (TABLESPOONS, 'Tablespoons'),
    ]

    units = models.CharField(max_length=10, choices=UNITS_CHOICES, default=GRAMS)

    def __str__(self):
        return "{} {} of {}".format(self.quantity, self.units, self.ingredient_name)

class Instruction(models.Model):
    objects = models.Manager()

    step = models.IntegerField(validators=[MinValueValidator(1)])
    instruction = models.TextField()
    uploads = models.ManyToManyField(blank=True, to=MediaUpload)

    def __str__(self):
        return "Step {}: {}".format(self.step, self.instruction)

class Comment(models.Model):
    """
    A comment has a
        - poster
        - content
        - last edited
    """
    objects = models.Manager()

    poster = models.ForeignKey(to=User, related_name='comments', on_delete=models.CASCADE)
    recipe = models.ForeignKey(to='Recipe', related_name='recipe_comments', on_delete=models.CASCADE)
    content = models.TextField(max_length=140)
    uploads = models.ManyToManyField(blank=True, to=MediaUpload)

    last_edited = models.TimeField(auto_now=True)

    # one-to-many relationship: comments have replies
    # note: not all comments are replies, mark as optional
    reply_to = models.ForeignKey(to='self', blank=True, null=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return "Comment by : {} (Reply to {})".format(self.poster, self.reply_to)


class Recipe(models.Model):
    """
    A recipe has a
        - creator
        - name
        - collection of diets
        - cuisine
        - serving size
        - prep time
        - media gallery

    """
    objects = models.Manager()

    creator = models.ForeignKey(to=User, related_name='recipes', on_delete=models.CASCADE)
    name = models.CharField(unique=True, max_length=100)
    diets = models.ManyToManyField(to=Diet)
    cuisine = models.CharField(max_length=30)
    serving_size = models.IntegerField(validators=[MinValueValidator(1)])
    prep_time = models.TimeField()

    instructions = models.ManyToManyField(to=Instruction)
    ingredients = models.ManyToManyField(to=Ingredient)
    uploads = models.ManyToManyField(blank=True, to=MediaUpload)

    liked_by = models.ManyToManyField(to=User, editable=False, related_name='recipes_liked')
    rated_by = models.ManyToManyField(to=User, editable=False, related_name='recipes_rated', through='social.RatingRecord')
    purchased_by = models.ManyToManyField(to=User, editable=False, related_name='recipes_shopped', through='shopping.CartItem')

    def __str__(self):
        return "A {} recipe from {}".format(self.name, self.creator)