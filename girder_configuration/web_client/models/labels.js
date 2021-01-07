import _ from 'underscore';

import { restRequest } from '@girder/core/rest';

import AccessControlledModel from '@girder/core/models/AccessControlledModel';

var LabelModel = AccessControlledModel.extend({
    resourceName: 'configuration/label',
    defaults: {
        fill: 'rgba(0,0,0,0)',
        hotkey: '',
        label: '',
        line: 'rgb(0,0,0)'
    },

    save: function () {
        if (this.altUrl === null && this.resourceName === null) {
            throw new Error('An altUrl or resourceName must be set on the Model.');
        }

        var path, type;
        if (this.has('_id')) {
            path = (this.altUrl || this.resourceName) + '/' + this.get('_id');
            type = 'PUT';
        } else {
            path = (this.altUrl || this.resourceName);
            type = 'POST';
        }
        var data = {};
        _.each(this.keys(), function (key) {
            var value = this.get(key);
            /*
            if (!_.isObject(value)) {
                data[key] = value;
            }
             */
            data[key] = value;
        }, this);

        return restRequest({
            url: path,
            method: type,
            contentType: 'application/json',
            processData: false,
            data: JSON.stringify(data)
        }).done((resp) => {
            this.set(resp);
            this.trigger('g:saved');
        }).fail((err) => {
            this.trigger('g:error', err);
        });
    }
});

export default LabelModel;
