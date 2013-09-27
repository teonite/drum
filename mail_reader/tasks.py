import logging
from celery import task
from django_mailbox.models import Mailbox
from settings import MAIL_CONFIG

import re
from main.models import Link
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

@task()
def checkMail():
    """
    Celery task: checks mailbox for new emails with links.
    If found, adds links to db.
    """
    logger.debug("Checking for new mail")
    boxes = Mailbox.objects.filter(name=MAIL_CONFIG["name"])
    if boxes.count() == 0:
        mailBox = Mailbox(name=MAIL_CONFIG["name"], uri=MAIL_CONFIG["uri"])
        mailBox.save()
    else:
        mailBox = boxes[0]

    logger.debug("Retrieving new mail from mailbox: " + mailBox.name)        
    newMessages = mailBox.get_new_mail()

    if newMessages:
        logger.info('[' + mailBox.name + '] Got new messages: ' + str(newMessages))
    
    for msg in newMessages:
        # find user for given email address
        try:
            user = User.objects.get(email=msg.from_address[0])
        except User.DoesNotExist:
            logger.warning('Got email from unknown user: ' + msg.from_address[0] + '. Ignoring.')
            continue

        # extract url from message
        url = re.search("(?P<url>https?://[^\s]+)", msg.get_text_body())
        if url:
            url = url.group("url")
        else:
            logger.warning('Got email without url from user: ' + user.username + '. Ignoring.')
            continue
        
        # extract description from message        
        description = re.sub(r'https?:\/\/[^\s]+', '', msg.get_text_body(), flags=re.MULTILINE)

        link = Link(user=user, title=msg.subject, link=url, description=description)
        
        # don't let mezzanine screw up our description
        link.gen_description = False

        link.save()
        logger.info('User ' + user.username + ' added new link by email: ' + url)
        