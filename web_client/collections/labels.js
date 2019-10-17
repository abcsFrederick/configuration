import Collection from 'girder/collections/Collection';

import LabelModel from '../models/labels';

export default Collection.extend({
    resourceName: 'configuration/label',
    model: LabelModel,
    sortField: 'index'
});
