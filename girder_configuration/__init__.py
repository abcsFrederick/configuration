import bson
import datetime
import json

from girder import plugin, events
from .rest import Configuration
from girder.constants import AccessType
from girder.settings import SettingDefault
from girder.utility import setting_utilities
from girder.utility.model_importer import ModelImporter

from girder.exceptions import ValidationException
from girder.models.item import Item
from girder.models.user import User as UserModel
from girder.models.notification import Notification

from girder_jobs.constants import JobStatus

from .constants import PluginSettings
from .models.labels import Labels

# from .models.annotationelementEx import AnnotationelementEx

# def _onUpload(event):
#     try:
#         ref = json.loads(event.info.get('reference', ''))
#     except (TypeError, ValueError):
#         return

#     if not isinstance(ref, dict):
#         return

#     if ref.get('isCellCounting'):
#         annotationElementsfileId = event.info['file']['_id']
#         user = event.info['currentUser']
#         token = event.info['currentToken']

#         try:
#             AnnotationelementEx().parseToAnnotationElement(annotationElementsfileId, user)
#         except (TypeError, ValueError):
#             return
#         Notification().createNotification(
#                 type='count_number_of_cell', data=ref, user=user,
#                 expires=datetime.datetime.utcnow() + datetime.timedelta(seconds=30))

@setting_utilities.validator({
    PluginSettings.DEFAULT_BEHAVIOR,
})
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

class ConfigurationPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'configuration'
    CLIENT_SOURCE_PATH = 'web_client'
    def load(self, info):
        ModelImporter.registerModel('labels', Labels, 'configuration')
        info['apiRoot'].configuration = Configuration()
        # events.bind('data.process', info['name'], _onUpload)