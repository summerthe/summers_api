from typing import Type

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from apps.news.models import Category


@receiver(post_save, sender=Category)
def slugify_category(
    sender: Type[Category],
    instance: Category,
    *args,
    **kwargs,
) -> None:
    """Slugify Category using its title.

    Parameters
    ----------
    sender : Type[Category]
    instance : Category
    """
    if kwargs["created"]:
        instance.slug = slugify(instance.title)
        instance.save()
