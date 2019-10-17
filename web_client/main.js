import './routes';

import { registerPluginNamespace } from 'girder/pluginUtils';

import * as configuration from './index';

registerPluginNamespace('configuration', configuration);
