import _ from 'underscore';
import Mousetrap from 'mousetrap';

import View from 'girder/views/View';
// import events from 'girder_plugins/HistomicsTK/events';
import { restRequest } from 'girder/rest';
import events from 'girder/events';

import configurationTemplate from '../templates/views/configurationTemplate.pug';
import LabelCollection from '../collections/labels';

var ConfigView = View.extend({
    events: {
        'click .h-configure-adding-behavior': '_changeBehavior'
    },
    initialize: function (settings) {
        this.collection = new LabelCollection();

        this.collection.fetch().done(() => {
            // eslint-disable-next-line
            _.each(this.collection.models, (model) => {
                let data = {};
                // data._id = model.get('_id');
                data.id = model.get('label');
                data.label = {value: model.get('label')};
                data.group = model.get('label');
                data.fillColor = model.get('fill');
                data.lineColor = model.get('line');
                let current = model.get('current');

                if (current) {
                    this.parentView._style.set(data);
                }
                this.parentView._groups.add(data);
            });
            this._keyboardBind();
        });
        // this.parentView._style.set(
        //     this.parentView._groups.get('Tumor').toJSON()
        //     );
        ConfigView.getSettings((settings) => {
            this.settings = settings;
            this.render();
        });
        this.listenTo(this.parentView._style, 'change', this._updateCurrent);
    },
    render() {
        this.$el.append(configurationTemplate({
            currentBehavior: this.settings['configuration.default_behavior']
        }));

        return this;
    },
    _changeBehavior: function (e) {
        var settings;
        if ($(e.currentTarget).val() === 'mouseUp') {
            this.$('.h-configure-adding-behavior').children().removeClass('icon-up-hand');
            this.$('.h-configure-adding-behavior').children().addClass('icon-location');
            $('.h-configure-adding-behavior').children().attr('title', 'At mouse up');
            this.$('.h-configure-adding-behavior').val('closeTo');
            settings = [{
                key: 'configuration.default_behavior',
                value: 'closeTo'
            }];
        } else {
            this.$('.h-configure-adding-behavior').children().removeClass('icon-location');
            this.$('.h-configure-adding-behavior').children().addClass('icon-up-hand');
            $('.h-configure-adding-behavior').children().attr('title', 'At closed to');
            this.$('.h-configure-adding-behavior').val('mouseUp');
            settings = [{
                key: 'configuration.default_behavior',
                value: 'mouseUp'
            }];
        }
        /* Now save the settings */
        return restRequest({
            type: 'PUT',
            url: 'system/setting',
            data: {
                list: JSON.stringify(settings)
            },
            error: null
        }).done(() => {
            /* Clear the settings that may have been loaded. */
            ConfigView.clearSettings();
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Settings saved.',
                type: 'success',
                timeout: 4000
            });
        }).fail((resp) => {
            this.$('#g-histogram-settinsge-error-message').text(
                resp.responseJSON.message
            );
        });
    },
    // FIX: multiple events are binded which bring duplicate.
    _keyboardBind: function () {
        let element = $('.h-image-view-container.geojs-map.highlight-focus')[0];
        // console.log($._data( element, 'events' ));
        this.m_keyHandler = Mousetrap(element);
        // eslint-disable-next-line
        _.each(this.collection.models, (label) => {
            this.m_keyHandler.bind(label.get('hotkey'), _.bind(function () {
                this.parentView.$('.h-style-group').val(label.get('label'));
                this.parentView._style.set(
                    this.parentView._groups.get(this.parentView.$('.h-style-group').val()).toJSON()
                );
            }, this));
        });
    },
    _updateCurrent: function () {
        let labelName = this.parentView._style.get('id');

        let label = this.collection.findWhere({label: labelName});

        if (label !== undefined) {
            label.set({current: true}).save();
        }
    },
    unbindKeyboard: function () {
    }
}, {
    /**
     * Get settings if we haven't yet done so.  Either way, call a callback
     * when we have settings.
     *
     * @param {function} callback a function to call after the settings are
     *      fetched.  If the settings are already present, this is called
     *      without any delay.
     */
    getSettings: function (callback) {
        // if (!ConfigView.settings) {
        restRequest({
            type: 'GET',
            url: 'configuration/settings'
        }).done((resp) => {
            ConfigView.settings = resp;
            if (callback) {
                callback(ConfigView.settings);
            }
        });
        // } else {
        //     if (callback) {
        //         callback(ConfigView.settings);
        //     }
        // }
    },

    /**
     * Clear the settings so that getSettings will refetch them.
     */
    clearSettings: function () {
        delete ConfigView.settings;
    }
});

export default ConfigView;
