import logging
from celery import task
from django_mailbox.models import Mailbox
from settings import MAIL_CONFIG

import re
from main.models import Link
from django.contrib.auth.models import User
import settings

logger = logging.getLogger(__name__)

@task()
def checkMail():
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
        username = settings.USER_EMAILS.get(msg.from_address[0], None)
        if not username:
            logger.warning('Got email from unknown user: ' + msg.from_address[0] + '. Ignoring.')
            continue
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error('User ' + username + ' does not exist, check your settings.USER_EMAILS configuration')
            continue
        
        # extract url from message
        url = re.search("(?P<url>https?://[^\s]+)", msg.body)
        if url:
            url = url.group("url")
        else:
            logger.warning('Got email without url from user: ' + username + '. Ignoring.')
            continue
        
        # extract description from message        
        description = re.sub(r'^https?:\/\/.*[\r\n]*', '', msg.body, flags=re.MULTILINE)
        link = Link(user=user, title=msg.subject, link=url, description=description)

        link.save()
        logger.info('User ' + username + ' added new link: ' + url)
        