from girder.models.model_base import AccessControlledModel
from girder.constants import AccessType
import datetime


class Labels(AccessControlledModel):
    def initialize(self):
        self.name = 'labels'
        self.ensureIndices([
            'created',
            'creatorId',
        ])
        self.ensureTextIndex({
            'label': 10,
        })

        self.exposeFields(AccessType.READ, (
            '_id',
            'label',
            'line',
            'fill',
            'hotkey',
            'current'
        ))

    def addOrUpdateLabel(self, creator, label, line, fill, hotkey):
        now = datetime.datetime.utcnow()
        existing = self.findOne({'label': label})
        if existing:
            existing['updatedId'] = creator['_id']
            existing['created'] = now
            existing['fill'] = fill
            existing['line'] = line
            existing['hotkey'] = hotkey
            return self.save(existing)
        hotkeyExisting = existing = self.findOne({'hotkey': hotkey})
        if hotkeyExisting:
            hotkeyExisting['hotkey'] = ''
            self.save(hotkeyExisting)
        doc = {
            'creatorId': creator['_id'],
            'created': now,
            'updatedId': creator['_id'],
            'updated': now,
            'label': label,
            'line': line,
            'fill': fill,
            'hotkey': hotkey,
            'current': False
        }

        return self.save(doc)

    def updateLabel(self, label, current=None, user=None):
        label['updated'] = datetime.datetime.utcnow()
        if user is not None:
            label['updatedId'] = user['_id']
        if current:
            currentLabel = self.findOne({'current': current})
            if currentLabel:
                currentLabel['current'] = False
                self.save(currentLabel)
            label['current'] = current
        return self.save(label)

    def validate(self, doc):
        return doc
