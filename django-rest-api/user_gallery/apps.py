from django.apps import AppConfig
from django.db.models.signals import post_migrate
#import logging

class UserGalleryConfig(AppConfig):
    name = 'user_gallery'

    def ready(self):
        from .utils import add_admin_user
        post_migrate.connect(add_admin_user, sender=self)
