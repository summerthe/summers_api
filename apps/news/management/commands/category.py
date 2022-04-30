from django.core.management.base import BaseCommand

from apps.news.models import Category


class Command(BaseCommand):
    help = "Create initial categories for articles"

    def handle(self, *args, **options):
        categories_list = [
            "Business",
            "Entertainment",
            "General",
            "Health",
            "Science",
            "Sports",
            "Technology",
        ]

        for category in categories_list:
            Category.objects.get_or_create(title=category)

        print(f"Created/updated {len(categories_list)} categories")
