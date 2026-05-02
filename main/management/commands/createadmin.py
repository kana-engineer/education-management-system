import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin user from ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME in .env'

    def handle(self, *args, **options):
        from dotenv import load_dotenv
        load_dotenv()
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        admin_name = os.getenv('ADMIN_NAME', 'Администратор')
        if not admin_email or not admin_password:
            self.stdout.write(self.style.WARNING('Add ADMIN_EMAIL and ADMIN_PASSWORD to .env'))
            return
        if User.objects.filter(email=admin_email).exists():
            user = User.objects.get(email=admin_email)
            if not user.check_password(admin_password):
                user.set_password(admin_password)
                user.save()
                self.stdout.write(self.style.SUCCESS('Admin password updated'))
            else:
                self.stdout.write('Admin already exists')
            return
        User.objects.create_superuser(email=admin_email, password=admin_password, name=admin_name)
        self.stdout.write(self.style.SUCCESS(f'Admin created: {admin_email}'))
