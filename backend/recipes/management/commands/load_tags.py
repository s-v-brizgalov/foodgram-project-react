from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Тэги'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#008000', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#800000', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#000080', 'slug': 'dinner'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Тэги успешно загружены!'))
