import AnnotationPopover from 'girder_plugins/HistomicsTK/views/popover/AnnotationPopover';

function point(p) {
    return `(${parseInt(p[0])}, ${parseInt(p[1])})`;
}

function length(p) {
    return `${Math.ceil(p)} px`;
}

function rotation(r) {
    return `${parseInt(r * 180 / Math.PI)}°`;
}

function Num_of_Cell(n) {
    return `${n}`;
}

var AnnotationPopoverEx = AnnotationPopover.extend({
    _elementProperties(element) {
        // cache the popover properties to reduce
        // computations on mouse move
        if (element._popover) {
            return element._popover;
        }

        function setIf(key, func = (v) => v) {
            const value = element.get(key);
            if (value) {
                props[key] = func(value);
            }
        }

        const props = {};
        element._popover = props;

        if (element.get('label')) {
            props.label = element.get('label').value;
        }
        if (element.get('group')) {
            props.group = element.get('group');
        }
        setIf('center', point);
        setIf('width', length);
        setIf('height', length);
        setIf('rotation', rotation);
        setIf('Num_of_Cell', Num_of_Cell);
        
        return props;
    },
});

export default AnnotationPopoverEx;