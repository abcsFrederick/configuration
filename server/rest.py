from girder import logger
from girder.api import access
from girder.constants import AccessType, TokenScope
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, filtermodel
from girder.models.setting import Setting
from girder.models.model_base import ValidationException
from girder.exceptions import RestException
from .constants import PluginSettings
from .models.labels import Labels


class Configuration(Resource):
    def __init__(self):
        super(Configuration, self).__init__()

        self.resourceName = 'configuration'
        self.route('POST', ('label',), self.addDefination)
        self.route('GET', ('label',), self.getLabels)
        self.route('PUT', ('label', ':id',), self.updateDefination)
        self.route('DELETE', ('label', ':id',), self.deleteDefination)
        self.route('GET', ('settings',), self.getSettings)

    @access.user(scope=TokenScope.DATA_WRITE)
    @filtermodel(model='labels', plugin='configuration')
    @autoDescribeRoute(
        Description('predefine a label.')
        .responseClass('configuration')
        .param('body', 'A JSON object containing the label.', paramType='body')
        # .param('label', 'Name for the label.', required=True, strip=True)
        # .param('line', 'Line color for the label', required=True, default='rgb(0,0,0)')
        # .param('fill', 'Fill color for the label', required=True, default='rgba(0,0,0,0)')
        # .param('hotkey', 'Hot key for the label', required=False)
        .errorResponse('Write access was denied for the label.', 403)
    )
    def addDefination(self, params):
        labelBody = self.getBodyJson()
        label = labelBody['label']
        line = labelBody['line']
        fill = labelBody['fill']
        hotkey = labelBody['hotkey']
        try:
            return Labels().addOrUpdateLabel(self.getCurrentUser(), label, line, fill, hotkey)
        except ValidationException as exc:
            logger.exception('Failed to validate label')
            raise RestException(
                'Validation Error: JSON doesn\'t follow schema (%r).' % (
                    exc.args, ))

    @access.user
    @filtermodel(model='labels', plugin='configuration')
    @autoDescribeRoute(
        Description('update a label.')
        .modelParam('id', model='labels', plugin='configuration',
                    level=AccessType.WRITE)
        .param('body', 'A JSON object containing the label.',
               paramType='body')
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the label.', 403)
    )
    def updateDefination(self, labels, params):
        user = self.getCurrentUser()
        update = self.getBodyJson()
        current = None
        if 'fill' in update:
            labels['fill'] = update['fill']
        if 'line' in update:
            labels['line'] = update['line']
        if 'hotkey' in update:
            labels['hotkey'] = update['hotkey']
        if 'current' in update:
            current = update['current']

        return Labels().updateLabel(labels, current, user=user)

    @access.user(scope=TokenScope.DATA_OWN)
    @filtermodel(model='labels', plugin='configuration')
    @autoDescribeRoute(
        Description('Delete a label.')
        .modelParam('id', model='labels', plugin='configuration',
                    level=AccessType.WRITE)
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the label.', 403)
    )
    def deleteDefination(self, labels):
        Labels().remove(labels)

    @access.public
    @autoDescribeRoute(
        Description('Getting Configuration settings.')
    )
    def getSettings(self):
        settings = Setting()
        return {
            PluginSettings.DEFAULT_BEHAVIOR:
                settings.get(PluginSettings.DEFAULT_BEHAVIOR),
        }

    @access.public
    @autoDescribeRoute(
        Description('Getting predefined label(s).')
        .param('label', 'Name for the label.', required=False)
    )
    def getLabels(self, params):
        query = {}
        if params['label'] is not None:
            query['label'] = params['label']
        return list(Labels().find(query))
