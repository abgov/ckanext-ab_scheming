import pylons.config as config
import ckan.logic as logic
import ckanext.ab_scheming.helpers as helpers
import ckan.plugins.toolkit as toolkit
from ckan.logic.action import create

NotFound = logic.NotFound


def package_create(context, data_dict):
    deployment_mode = toolkit.asbool(config.get('ckan.ab_scheming.deployment', False))
    # need to change data_dict if import from ckanapi
    if deployment_mode:
        data_dict = change_pkg_dict_for_import_deployment(data_dict)
    return create.package_create(context, data_dict)


def change_pkg_dict_for_import_deployment(data_dict):
    if 'topic' in data_dict:
        data_dict['topics'] = data_dict['topic']
        del data_dict['topic']
    if 'extras' in data_dict:
        for e in data_dict['extras']:
            if 'topic' == e['key']:
                e['key'] = 'topics'
                break
    if 'id' in data_dict:
        del(data_dict['id'])
    if 'groups' in data_dict:
        for ind, g in enumerate(data_dict['groups']):
            if g.has_key('id'):
                del(data_dict['groups'][ind]['id'])
    if 'tags' in data_dict:
        for ind, t in enumerate(data_dict['tags']):
            if t.has_key('id'):
                del(data_dict['tags'][ind]['id'])
    if 'revision_id' in data_dict:
        del(data_dict['revision_id'])
    if 'organization' in data_dict:
        if data_dict['organization'].has_key('id'):
            del(data_dict['organization']['id'])
        if data_dict['organization'].has_key('revision_id'):
            del(data_dict['organization']['revision_id'])
    if 'owner_org' in data_dict:
        try:
            data_dict['organization']['name']
        except KeyError:
            raise NotFound('Could not find organization name in dataset {0}'.format(data_dict['name']))
        else:
            data_dict['owner_org'] = data_dict['organization']['name']

    if 'resources' in data_dict:
        for ind, r in enumerate(data_dict['resources']):
            if r.has_key('id'):
                del(data_dict['resources'][ind]['id'])
            if r.has_key('package_id'):
                del(data_dict['resources'][ind]['package_id'])

    all_required_fields = helpers.get_required_fields_name(data_dict['type'])
    for f in all_required_fields:
        if not exist_field_in_pkg_dict(f, data_dict):
            data_dict[f] = ''

    return data_dict


def exist_field_in_pkg_dict(field, data_dict):
    if field in data_dict:
        return True
    if 'extras' in data_dict:
        for pair in data_dict['extras']:
            if field == pair['key']:
                return True
    return False