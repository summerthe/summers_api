from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.news"
    verbose_name = _("News")

    def ready(self) -> None:
        from apps.news.models import Category
        from apps.news.signals import slugify_category

        post_save.connect(slugify_category, sender=Category)
