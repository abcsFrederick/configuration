import './routes';

import { registerPluginNamespace } from '@girder/core/pluginUtils';

import * as configuration from './index';

registerPluginNamespace('configuration', configuration);
