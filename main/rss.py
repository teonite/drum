from django.contrib.syndication.views import Feed
from models import Link

class LatestLinksFeed(Feed):
    title = "Drum latest feeds"
    link = "/newest/"
    description = "Shows new links"

    def items(self):
        return Link.objects.order_by('-publish_date')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.link
