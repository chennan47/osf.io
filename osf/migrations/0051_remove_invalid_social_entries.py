# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-10 12:35
from __future__ import unicode_literals

from django.db import migrations

from osf.models import OSFUser as osfuser

import logging

logger = logging.getLogger(__file__)

def remove_invalid_social_entries(state, *args, **kwargs):
    OSFUser = state.get_model('osf', 'osfuser')
    # targets = OSFUser.objects.filter()
    targets = OSFUser.objects.exclude(social={})

    logger.info('Removing invalid social entries!')

    for user in targets:
        for invalid_key in set(user.social.keys()) - set(osfuser.SOCIAL_FIELDS.keys()):
                logger.warn(str(dir(user)))
                user.social.pop(invalid_key)
                logger.info('User ID {0}: dropped social: {1}'.format(user.id, invalid_key))
                user.save()

    logger.info('Invalid social entry removal completed.')

class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0050_auto_20170809_1511'),
    ]

    operations = [
        migrations.RunPython(remove_invalid_social_entries)
    ]
