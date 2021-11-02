from django.contrib import admin
from .models import User, Album, Photo, Comment, Bookmark
# Register your models here.

class AuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, AuthorAdmin)
admin.site.register(Album, AuthorAdmin)
admin.site.register(Photo, AuthorAdmin)
admin.site.register(Comment, AuthorAdmin)
admin.site.register(Bookmark, AuthorAdmin)
