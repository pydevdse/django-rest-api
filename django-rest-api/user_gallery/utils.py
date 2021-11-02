import os
#import logging

def add_admin_user(sender, **kwargs):
    from .models import User
    User.objects.filter(is_superuser=True).delete()
    admin_email = os.environ.get('ADMIN_DB_EMAIL')
    admin = os.environ.get('ADMIN_DB')
    admin_password = os.environ.get('ADMIN_DB_PASSWORD')
    u = User.objects.create_superuser(email=admin_email, username=admin, password=admin_password)
