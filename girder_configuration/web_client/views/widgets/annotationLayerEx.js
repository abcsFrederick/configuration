function registerAnnotationLayer(geo) {
    geo.annotationLayerEx = function (args) {
        // Constructors take a single object to hold options passed to each
        // constructor in the class hierarchy.  The default is usually an
        // empty object.
        args = args || {};
        // Here we handle calling the constructor again with a new object
        // when necessary.
        if (!(this instanceof geo.annotationLayerEx)) {
            // eslint-disable-next-line
            return new geo.annotationLayerEx(args);
        }

        geo.annotationLayer.call(this, args);
        // eslint-disable-next-line
        var m_this = this,
            // eslint-disable-next-line
            s_func = this.func;
        this._processAction = function (evt) {
            var update;
            if (evt.state && evt.state.actionRecord &&
                evt.state.actionRecord.owner === geo.annotation.actionOwner &&
                m_this.currentAnnotation) {
                switch (m_this.mode()) {
                    case m_this.modes.edit:
                        update = m_this.currentAnnotation.processEditAction(evt);
                        if (m_this.currentAnnotation &&
                            m_this.currentAnnotation._editHandle &&
                            m_this.currentAnnotation._editHandle.handle) {
                            m_this.geoTrigger(geo.event.annotation.edit_action, {
                                annotation: m_this.currentAnnotation,
                                handle: m_this.currentAnnotation._editHandle ? m_this.currentAnnotation._editHandle.handle : undefined,
                                action: evt.event
                            });
                            if (evt.event === geo.event.actionup) {
                                m_this._selectEditHandle(
                                    {data: m_this.currentAnnotation._editHandle.handle},
                                    m_this.currentAnnotation._editHandle.handle.selected);
                            }
                        }
                        break;
                    default:
                        update = m_this.currentAnnotation.processAction(evt);
                        if (evt.event === geo.event.actionup) {
                            let vertices = m_this.currentAnnotation.options('vertices');
                            // Only for polygon
                            if (evt.state.action === 'geo_annotation_polygon') {
                                if ($('.h-configure-adding-behavior').val() === 'closeTo') {
                                    if (vertices.length >= 3 && m_this.displayDistance(
                                        vertices[0], null, evt.mouse.map, 'display') <=
                                        m_this.options('finalPointProximity')) {
                                        vertices.pop();
                                        m_this.currentAnnotation.state(geo.annotation.state.done);
                                        update = geo.annotation.state.done;
                                    }
                                } else {
                                    vertices.pop();
                                    m_this.currentAnnotation.state(geo.annotation.state.done);
                                    update = geo.annotation.state.done;
                                }  
                            }
                        }
                        break;
                }
            }
            m_this._updateFromEvent(update);
        };
    };
    // Initialize the class prototype.
    geo.inherit(geo.annotationLayerEx, geo.annotationLayer);

    geo.registerLayer('annotationEx', geo.annotationLayerEx);
}

export default registerAnnotationLayer;
