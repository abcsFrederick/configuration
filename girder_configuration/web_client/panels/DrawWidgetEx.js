import DrawWidget from '@girder/histomicsui/panels/DrawWidget';
import { wrap } from '@girder/core/utilities/PluginUtils';

import ConfigurationView from '../views/ConfigurationView';

import drawWidget from '@girder/histomicsui/templates/panels/drawWidget.pug';


wrap(DrawWidget, 'render', function (render) {
    this.$('[data-toggle="tooltip"]').tooltip('destroy');
    if (!this.viewer) {
        this.$el.empty();
        delete this._skipRenderHTML;
        return;
    }
    const name = (this.annotation.get('annotation') || {}).name || 'Untitled';
    this.trigger('h:redraw', this.annotation);
    if (this._skipRenderHTML) {
        delete this._skipRenderHTML;
    } else {
        this.$el.html(drawWidget({
            title: 'Draw',
            elements: this.collection.models,
            groups: this._groups,
            style: this._style.id,
            highlighted: this._highlighted,
            name
        }));
        this.ConfigurationView = new ConfigurationView({
            el: this.$('.h-style-group-row'),
            parentView: this
        });
    }
    if (this._drawingType) {
        this.$('button.h-draw[data-type="' + this._drawingType + '"]').addClass('active');
        this.drawElement(undefined, this._drawingType);
    }
    this.$('.s-panel-content').collapse({toggle: false});
    this.$('[data-toggle="tooltip"]').tooltip({container: 'body'});
    if (this.viewer.annotationLayer && !this.viewer.annotationLayer._boundHistomicsTKModeChange) {
        this.viewer.annotationLayer._boundHistomicsTKModeChange = true;
        this.viewer.annotationLayer.geoOn(window.geo.event.annotation.mode, (event) => {
            this.$('button.h-draw').removeClass('active');
            if (this._drawingType) {
                this.$('button.h-draw[data-type="' + this._drawingType + '"]').addClass('active');
            }
            if (event.mode !== this._drawingType && this._drawingType) {
                /* This makes the draw modes stay on until toggled off.
                 * To turn off drawing after each annotation, add
                 *  this._drawingType = null;
                 */
                this.drawElement(undefined, this._drawingType);
            }
        });
    }
    return this;
});

export default DrawWidget;