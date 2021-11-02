from django.contrib import admin
from .models import User
# Register your models here.

class AuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, AuthorAdmin)