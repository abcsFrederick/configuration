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

from .rest import Configuration
from girder.constants import SettingDefault
from girder.utility import setting_utilities
from girder.exceptions import ValidationException
from .constants import PluginSettings


@setting_utilities.validator({
    PluginSettings.DEFAULT_BEHAVIOR,
})
def validateNonnegativeInteger(doc):
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
