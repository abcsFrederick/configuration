import DrawWidget from 'girder_plugins/HistomicsTK/panels/DrawWidget';
import { wrap } from 'girder/utilities/PluginUtils';

import ConfigurationView from './ConfigurationView';

wrap(DrawWidget, 'render', function (render) {
    render.call(this);
    if (this.ConfigurationView) {
        // console.log(this.ConfigurationView)
        // this.ConfigurationView.unbindKeyboard();
        this.ConfigurationView.destroy();
    }
    this.ConfigurationView = new ConfigurationView({
        el: this.$('.h-style-group-row'),
        parentView: this
    });
    return this;
});
