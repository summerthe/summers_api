from django.contrib.auth import get_user_model
from django.contrib.sitemaps import Sitemap

User = get_user_model()


class UserViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1

    def items(self):
        return User.objects.all()

    def location(self, item):
        return f"/users/{item.pk}"
