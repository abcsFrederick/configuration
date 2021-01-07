import router from '@girder/core/router';

import events from '@girder/core/events';
import { exposePluginConfig } from '@girder/core/utilities/PluginUtils';

import ConfigView from './views/configView';

exposePluginConfig('configuration', 'plugins/configuration/config');

router.route('plugins/configuration/config', 'configurationConfig', function () {
    events.trigger('g:navigateTo', ConfigView);
});
