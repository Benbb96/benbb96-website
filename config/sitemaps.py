from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    changefreq = "monthly"

    # Les pages légales doivent être trouvables, mais sans concurrencer la home
    # et « à propos » dans l'index.
    LOW_PRIORITY = {"base:privacy", "base:legal-notice"}

    def items(self):
        return ["base:home", "base:about", "base:privacy", "base:legal-notice"]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 0.3 if item in self.LOW_PRIORITY else 0.8
