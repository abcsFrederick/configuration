// import GeojsViewer from 'girder_plugins/large_image/views/imageViewerWidget/geojs';
import { ViewerWidget } from '@girder/large_image_annotation/views';
import { wrap } from '@girder/core/utilities/PluginUtils';

import registerAnnotationLayer from './widgets/annotationLayerEx';
import registerLayer from './widgets/osmLayerEx';

window.test = ViewerWidget['geojs']
wrap(ViewerWidget['geojs'], 'render', function (render) {
    render.call(this);
    var geo = window.geo;

    if (!geo.registries.layers.annotationEx) {
        registerLayer(geo);
        registerAnnotationLayer(geo);
        this.annotationLayer = this.viewer.createLayer('annotationEx', {
            annotations: ['point', 'line', 'rectangle', 'polygon'],
            showLabels: false
        });
    }

    return this;
});
