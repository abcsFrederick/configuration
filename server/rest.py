import bson
import json
import ujson
import os 
import six.moves.urllib.request
import requests

from girder import logger
from girder.api import access
from girder.constants import AccessType, TokenScope, SortDir
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, filtermodel, setResponseHeader
from girder.models.setting import Setting
from girder.utility import JsonEncoder
from girder.models.model_base import ValidationException
from girder.exceptions import RestException
from girder.models.file import File

from .constants import PluginSettings
from .models.labels import Labels
from girder.plugins.large_image.models.annotation import AnnotationSchema, Annotation
from girder.plugins.large_image.rest.annotation import AnnotationResource
from girder.plugins.large_image.models.annotationelement import Annotationelement
from girder.plugins.overlays.models.overlay import Overlay
from girder.plugins.jobs.models.job import Job
from girder.plugins.worker import utils


class Configuration(Resource):
    def __init__(self):
        super(Configuration, self).__init__()

        self.resourceName = 'configuration'
        self.route('POST', ('label',), self.addDefination)
        self.route('GET', ('label',), self.getLabels)
        self.route('PUT', ('label', ':id',), self.updateDefination)
        self.route('DELETE', ('label', ':id',), self.deleteDefination)
        self.route('GET', ('settings',), self.getSettings)

        self.route('POST', ('count', 'label', ':id',), self.count)

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

    @access.user
    @autoDescribeRoute(
        Description('update a label.')
        .param('id', 'The ID of the annotation.', paramType='path')
    )
    def count(self, id):
        user = self.getCurrentUser()
        token = self.getCurrentToken()

        annotation = Annotation().load(
            id, user=user, level=AccessType.READ, getElements=False)
        if annotation is None:
            raise RestException('Annotation not found', 404)
        annotation = Annotation().filter(annotation, self.getCurrentUser())

        request = utils.getWorkerApiUrl() + '/annotation/' + id
        headers = {'Girder-Token': token['_id']}
        resp = requests.get(request, headers=headers)
        # print resp.json()
        # function
        # elements = AnnotationResource().getAnnotation(id, params={})
        elements = resp.json()['annotation']['elements']

        imageId = annotation['itemId']
        sort = [
            ('itemId', SortDir.ASCENDING),
            ('index', SortDir.ASCENDING),
            ('created', SortDir.ASCENDING),
        ]
        query = {}
        query['itemId'] = str(imageId)
        overlays = list(Overlay().filterResultsByPermission(
            cursor=Overlay().find(query, sort=sort),
            user=user,
            level=AccessType.READ,
            limit=1, offset=0
        ))
        print overlays
        try:
            # For now assume there is just one overlay
            overlay = overlays[0]
        except:
            raise RestException('There is no overlay for this WSI.')
        overlayItem = overlay['overlayItemId']

        query = {
            'itemId': bson.objectid.ObjectId(overlayItem),
            'mimeType': {'$regex': '^image/tiff'}
        }
        files = list(File().find(query, limit=2))
        if len(files) >= 1:
            fileId = str(files[0]['_id'])
        if not fileId:
            raise RestException('Missing "fileId" parameter.')

        file_ = File().load(fileId, user=user, level=AccessType.READ, exc=True)


        path = os.path.join(os.path.dirname(__file__), '../scripts/',
                            'countCell.py')
        with open(path, 'r') as f:
            script = f.read()

        title = 'Count number of cell for overlay %s' % overlay['_id']
        job = Job().createJob(title=title, type='countCell',
                              handler='worker_handler', user=user)
        jobToken = Job().createJobToken(job)

        task = {
            'mode': 'python',
            'script': script,
            'name': title,
            'inputs': [{
                'id': 'in_path',
                'target': 'filepath',
                'type': 'string',
                'format': 'text'
            }, {
                'id': 'elements',
                'type': 'string',
                'format': 'text',
            }],
            'outputs': [{
                'id': 'elementsWithCell',
                'target': 'memory',
                'type': 'string',
                'format': 'text',
            }],
        }
        inputs = {
            'in_path': utils.girderInputSpec(
                file_, resourceType='file', token=token),
            'elements': {
                'mode': 'inline',
                'type': 'string',
                'format': 'text',
                'data': elements,
            }
        }

        outputs = {
            # 'elementsWithCell': {
            #     'mode': 'inline',
            #     'type': 'string',
            #     'format': 'text'
            # }
            'elementsWithCell': {
                "mode": "girder",
                "as_metadata": True,
                "item_id": str(overlayItem),
                "api_url": utils.getWorkerApiUrl(),
                "token": token['_id']
            }
        }
        job['kwargs'] = {
            'task': task,
            'inputs': inputs,
            'outputs': outputs,
            'jobInfo': utils.jobInfoSpec(job, jobToken),
            'auto_convert': True,
            'validate': True,
        }

        job['meta'] = {
            'creator': 'countCell',
            'task': 'countCell',
        }

        job = Job().save(job)

        Job().scheduleJob(job)
        # return createHistogramJob(item, file_, user=user,
        #                           token=token, notify=notify,
        #                           bins=bins, label=label,
        #                           bitmask=bitmask)
