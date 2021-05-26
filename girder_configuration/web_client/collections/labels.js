import Collection from '@girder/core/collections/Collection';

import LabelModel from '../models/labels';

export default Collection.extend({
    resourceName: 'configuration/label',
    model: LabelModel,
    sortField: 'index'
});
