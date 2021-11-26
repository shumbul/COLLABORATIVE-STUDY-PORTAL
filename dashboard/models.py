from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Notes(models.Model):
    # CASCADING for deleting user's details when user's account gets deleted from the Database
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length=200)
    desc = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Notes"
        verbose_name_plural = "Notes"

class Homework(models.Model):
    # fieldset
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length = 50)
    desc = models.TextField()
    due = models.DateTimeField()
    is_finished = models.BooleanField(default=False)

    # because Django-admin outs an extra "s" in the end,
    # we don't want that, thus freezing this title
    def __str__(self):
        return self.title

class Todo(models.Model):
    #fieldset
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length=100)
    desc = models.TextField()
    is_finished = models.BooleanField(default=False)

    # because Django-admin outs an extra "s" in the end,
    # we don't want that, thus freezing this title
    def __str__(self):
        return self.title


# class Profile(models.Model):
#     user = models.OneToOneField(User, null = True, on_delete = models.CASCADE)
#     bio = models.TextField()
#
#     def __str__(self):
#         return str(self.user)
