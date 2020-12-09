#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Girder plugin framework and tests adapted from Kitware Inc. source and
#  documentation by the Imaging and Visualization Group, Advanced Biomedical
#  Computational Science, Frederick National Laboratory for Cancer Research.
#
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################
import bson
import datetime

from girder import events
from .rest import Configuration
from girder.constants import SettingDefault, AccessType
from girder.utility import setting_utilities
from girder.exceptions import ValidationException
from girder.models.item import Item
from girder.models.user import User as UserModel
from girder.models.notification import Notification

from .constants import PluginSettings

from girder.plugins.jobs.constants import JobStatus
from girder.plugins.large_image.models.annotationelement import Annotationelement


@setting_utilities.validator({
    PluginSettings.DEFAULT_BEHAVIOR,
})

def _updateJob(event):
    if event.name == 'jobs.job.update.after':
        job = event.info['job']
    else:
        job = event.info
    meta = job.get('meta', {})
    if (meta.get('creator') != 'countCell' or
            meta.get('task') != 'countCell'):
        return
    status = job['status']
    if status not in (JobStatus.ERROR, JobStatus.CANCELED, JobStatus.SUCCESS):
        return
    if status == JobStatus.SUCCESS:
        if (meta.get('creator') == 'countCell' and
                meta.get('task') == 'countCell'):
            userId = job['userId']
            user = UserModel().load(userId, force=True, fields=['email'])
            itemId = job['kwargs']['outputs']['elementsWithCell']['item_id']
            item = Item().load(itemId, user=user, force=True)
            item_meta = item['meta']
            for annotationElementId in item_meta:
                query = {'element.id': str(annotationElementId)}
                annotationelements = list(Annotationelement().find(query=query))
                if len(annotationelements) != 0:
                    # update for all version
                    for annotationelement in annotationelements:
                        annotationelement['element'] = item_meta[annotationElementId]
                        Annotationelement().save(annotationelement, validate=False)

            for annotationElementId in item_meta:
                # delete previous meta in item
                query = {'element.id': str(annotationElementId)}
                annotationelements = list(Annotationelement().find(query=query))
                if len(annotationelements) == 0:
                    Item().deleteMetadata(item, [annotationElementId])

            Notification().createNotification(
                type='count_number_of_cell', data=job, user=user,
                expires=datetime.datetime.utcnow() + datetime.timedelta(seconds=30))

def validateActions(doc):
    val = doc['value']
    try:
        if val == 'mouseUp' or val == 'closeTo':
            doc['value'] = val
        else:
            raise ValueError
    except ValueError:
        msg = '%s must be mouseUp or closeTo.' % doc['key']
        raise ValidationException(msg, 'value')


SettingDefault.defaults.update({
    PluginSettings.DEFAULT_BEHAVIOR: 'mouseUp',
})


def load(info):
    info['apiRoot'].configuration = Configuration()

    events.bind('jobs.job.update.after', info['name'], _updateJob)