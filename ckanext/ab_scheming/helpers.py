from ckan.common import  c
import ckan.logic as logic
import  ckanext.scheming.helpers as h

def topics_available(permission='read'):
#    '''Return a list of organizations that the current user has the specified
#    permission for.
#    '''
    context = {'user': c.user}
#    data_dict = {'permission': permission}
#    return logic.get_action('topics_list_for_user')(context, data_dict)
    groups = logic.get_action('group_list')(context, {'type': 'topics',
                                                      'all_fields': True})
    ret = []
    for grp in groups:
        ret.append({'value': grp['name'], 'label': grp['display_name']})
    return ret

def get_required_fields_name(dataset_type):
    dataset_scheme = h.scheming_get_schema('dataset', dataset_type)
    fields = dataset_scheme['dataset_fields']
    required_fields_name = []
    for f in fields:
        if f.get('required'):
            required_fields_name.append(f.get('field_name'))
    return  required_fields_name
