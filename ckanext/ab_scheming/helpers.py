from ckan.common import  c
import ckan.logic as logic


def topics_available(permission='read'):
    '''Return a list of organizations that the current user has the specified
    permission for.
    '''
    context = {'user': c.user}
    data_dict = {'permission': permission}
    return logic.get_action('topics_list_for_user')(context, data_dict)