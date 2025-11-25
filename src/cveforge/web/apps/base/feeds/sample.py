from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.translation import gettext as _

from cveforge.web.apps.base.models import CVEModel


class LatestCVEFeed(Feed):
    title = _("Latest CVEs")
    link = "/cve/"
    description = "Latest uploaded CVEs from different providers"

    def items(self):
        return CVEModel.objects.all()

    def item_title(self, item: CVEModel):
        return "</description>hola<description>"# str(item)

    def item_description(self, item: CVEModel):
        return item.description

    def item_link(self, item):
        return ""
