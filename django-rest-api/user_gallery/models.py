from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField('first name', max_length=150, blank=True, null=True)
    last_name = models.CharField('last name', max_length=150, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_on"]
        
        
class Album(models.Model):
    name = models.CharField(max_length=120)
    owner = models.ForeignKey("User", related_name="albums", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_on"]


def user_directory_path(instance, filename):
    return "images/user_{0}/{1}".format(instance.owner.id, filename)


class Photo(models.Model):
    description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    album = models.ForeignKey("Album", related_name="photos", on_delete=models.CASCADE)
    owner = models.ForeignKey("User", related_name="photos", on_delete=models.CASCADE)
    image = models.FileField(upload_to=user_directory_path)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ["-created_on"]


class Comment(models.Model):
    text = models.CharField(max_length=120)
    photo = models.ForeignKey(
        "Photo", related_name="comments", on_delete=models.CASCADE
    )
    owner = models.ForeignKey("User", related_name="comments", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0}, text: {1}".format(str(self.owner), str(self.text))

    class Meta:
        ordering = ["-created_on"]


class Bookmark(models.Model):
    photo = models.ForeignKey(
        "Photo", related_name="bookmarks", on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        "User", related_name="bookmarks", on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.owner)
        
    class Meta:
        ordering = ["-created_on"]

    class Meta:
        ordering = ["-created_on"]
