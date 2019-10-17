import View from 'girder/views/View';

import PluginConfigBreadcrumbWidget from
    'girder/views/widgets/PluginConfigBreadcrumbWidget';

import LabelModel from '../models/labels';
import LabelCollection from '../collections/labels';
import ConfigViewTemplate from '../templates/views/configView.pug';

import '../stylesheets/views/configView.styl';

var ConfigView = View.extend({
    events: {
        'click #addLabel': function (event) {
            let label = $('.g-configuration-settings-label').val(),
                line = $('.colorpicker-component-line').val(),
                fill = $('.colorpicker-component-fill').val(),
                hotkey = $('.colorpicker-component-hotkey').val();
            this._predefineLabel(label, line, fill, hotkey);
        },
        'click .deleteLabel': '_deleteLabel'
    },
    initialize: function (settings) {
        this.collection = new LabelCollection();
        this.collection.fetch().done(() => {
            this.render();
        });
    },
    render: function () {
        this.$el.html(ConfigViewTemplate({
            // eslint-disable-next-line
            labels: this.collection.models
        }));
        if (!this.breadcrumb) {
            this.breadcrumb = new PluginConfigBreadcrumbWidget({
                pluginName: 'Configuration',
                el: this.$('.g-config-breadcrumb-container'),
                parentView: this
            }).render();
        } else {
            this.breadcrumb.destroy();
            this.breadcrumb = new PluginConfigBreadcrumbWidget({
                pluginName: 'Configuration',
                el: this.$('.g-config-breadcrumb-container'),
                parentView: this
            }).render();
        }
        $('.g-label-line-color').colorpicker({
            color: '#000000',
            format: 'rgb'
        });
        $('.g-label-fill-color').colorpicker({
            color: 'rgba(0,0,0,0)',
            format: 'rgba'
        });
        return this;
    },
    _predefineLabel(label, line, fill, hotkey) {
        this.model = new LabelModel();
        this.model.set({
            line: line,
            label: label,
            fill: fill,
            hotkey: hotkey
        }).on('g:saved', () => {
            this.collection.fetch().done(() => {
                this.render();
            });
        }).save();
    },
    _deleteLabel(e) {
        let id = $(e.currentTarget).attr('label-id');
        let label = this.collection.get(id);
        label.on('g:deleted', () => {
            this.collection.fetch().done(() => {
                this.render();
            });
        }).destroy();
    }
});

export default ConfigView;
