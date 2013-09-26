from urlparse import urlparse

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.contrib.sites.models import get_current_site

from mezzanine.core.models import Displayable, Ownable
from mezzanine.generic.models import Rating
from mezzanine.generic.fields import RatingField, CommentsField

from notification import models as notification


class Link(Displayable, Ownable):

    link = models.URLField()
    rating = RatingField()
    comments = CommentsField()

    @models.permalink
    def get_absolute_url(self):
        return ("link_detail", (), {"slug": self.slug})

    def domain(self):
        return urlparse(self.link).netloc


class Profile(models.Model):

    user = models.OneToOneField("auth.User")
    website = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    karma = models.IntegerField(default=0, editable=False)

    def __unicode__(self):
        return "%s (%s)" % (self.user, self.karma)


@receiver(post_save, sender=Rating)
def karma(sender, **kwargs):
    """
    Each time a rating is saved, check its value and modify the
    profile karma for the related object's user accordingly.
    Since ratings are either +1/-1, if a rating is being edited,
    we can assume that the existing rating is in the other direction,
    so we multiply the karma modifier by 2.
    """
    rating = kwargs["instance"]
    value = int(rating.value)
    if not kwargs["created"]:
        value *= 2
    content_object = rating.content_object
    if rating.user != content_object.user:
        queryset = Profile.objects.filter(user=content_object.user)
        queryset.update(karma=models.F("karma") + value)

@receiver(post_save, sender=Link)
def notify(sender, **kwargs):
    """
    Notifies users about new link by email
    """
    users = User.objects.all()
    link = kwargs['instance']
    
    url = ''.join(['http://', get_current_site(None).domain, reverse('link_detail', kwargs={'slug': link.slug})]) 
    
    notification.send(users, "new_link", 
                      {'user': link.user.username, 
                       'url': url})
    
    