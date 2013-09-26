from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from notification import models as notification

def create_notice_types(app, created_models, verbosity, **kwargs):
    notification.create_notice_type("new_link", _("New entry added to TNT HackerNews"), _("New entry added to TNT HackerNews"))

signals.post_syncdb.connect(create_notice_types, sender=notification)
