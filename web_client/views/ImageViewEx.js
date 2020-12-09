import ImageView from 'girder_plugins/HistomicsTK/views/body/ImageView';
import { wrap } from 'girder/utilities/PluginUtils';

import AnnotationPopoverEx from './widgets/AnnotationPopoverEx';

wrap(ImageView, '_removeDrawWidget', function (render) {
    if (this.drawWidget) {
        // To remove its children view
        this.drawWidget.destroy();
        this._lastDrawingType = this.drawWidget.drawingType();
        this.drawWidget.cancelDrawMode();
        this.stopListening(this.drawWidget);
        this.drawWidget.remove();
        this.drawWidget = null;
        $('<div/>').addClass('h-draw-widget s-panel hidden')
            .appendTo(this.$('#h-annotation-selector-container'));
    }
    return this;
});

wrap(ImageView, 'initialize', function (initialize) {
    initialize.call(this);
    this.popover = new AnnotationPopoverEx({
        parentView: this
    });
    return this;
});