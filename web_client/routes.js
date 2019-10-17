import router from 'girder/router';

import events from 'girder/events';
import { exposePluginConfig } from 'girder/utilities/PluginUtils';

import ConfigView from './views/configView';

exposePluginConfig('configuration', 'plugins/configuration/config');

router.route('plugins/configuration/config', 'configurationConfig', function () {
    events.trigger('g:navigateTo', ConfigView);
});
