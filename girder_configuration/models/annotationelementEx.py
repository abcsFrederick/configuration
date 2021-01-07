from girder.plugins.large_image.models.annotationelement import Annotationelement
from girder.constants import AccessType
from girder.models.file import File

import json
import datetime


class AnnotationelementEx(Annotationelement):
  def parseToAnnotationElement(self, fileId, user):
    annotationElementsfile = File().load(fileId, user=user)
    with File().open(annotationElementsfile) as json_file:
      data = json.load(json_file)
      for key in data.keys():
        print key
        query = {'element.id': str(key)}
        annotationelements = list(self.find(query=query))
        if len(annotationelements) != 0:
          # update for all version
          for annotationelement in annotationelements:
            annotationelement['element'] = data[key]
            self.save(annotationelement, validate=False)
    return True