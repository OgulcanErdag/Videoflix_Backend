from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a guest demo user if it does not exist.'

    def handle(self, *args, **kwargs):
        email = 'guest@example.com'
        password = 'Guest1234!'

        if not User.objects.filter(email=email).exists():
            User.objects.create_user(username='guest', email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Guest user created.'))
        else:
            self.stdout.write(self.style.WARNING('Guest user already exists.'))
