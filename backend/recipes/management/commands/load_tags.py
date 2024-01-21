from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Теги'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#ffd966', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#4a8685', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#dda3ad', 'slug': 'dinner'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Ok'))
