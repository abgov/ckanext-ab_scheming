
# -*- coding: utf-8 -*-
import ckanext.ab_scheming.helpers as helpers
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import datetime

NotFound = logic.NotFound 

GROUP_NAME_MATCH = {
    'employmentandimmigration2008-2011': 'employmentandimmigration-2008-2011',
    'aboriginalrelations': 'aboriginalrelations2008-2011--2013-2016',
    'jobsskillstrainingandlabour': 'jobsskillstrainingandlabour2013-2016',
    'seniors': 'seniors2001-2004--2011-2013--2014-2016',
    'jobsskillstrainingandlabour-2013-2016': 'jobsskillstrainingandlabour2013-2016',
    'seniors-2001-2004-2011-2013-2014-2016': 'seniors2001-2004--2011-2013--2014-2016',
    'aboriginalrelations-2008-2011-2013-2016': 'aboriginalrelations2008-2011--2013-2016'
}

TOPICS_NAME_MATCH = {
    'Education - Post-Secondary and Skills Training': 'Education - Post - Secondary and Skills Training',
    'Employment And Labour': 'Employment and Labour',
    'seniors': 'Seniors'
}

CREATOR_MATCH = {
    'Culture (1980-1987, 2013-2014)': 'Culture (1980-1987, 2012-2014)',
    'Health and Wellness (1999-2013)': 'Health and Wellness (1999-2012)',
    'Culture and Community Services (2011-2013)': 'Culture and Community Services (2011-2012)',
    'Environment and Water (2011-2013)': 'Environment and Water (2011-2012)',
    'Solicitor General and Public Security (1973-1992, 2001-2006, 2008-2013)': 'Solicitor General and Public Security (1973-1992, 2001-2006, 2008-2012)',
    'Sustainable Resource Development (2001-2006, 2006-2013)': 'Sustainable Resource Development (2001-2006, 2006-2012)',
    'Jobs, Skills, Training and Labour': 'Jobs, Skills, Training and Labour (2013-2016)',
    'Jobs,Skills,TrainingandLabour': 'Jobs, Skills, Training and Labour (2013-2016)', 
    'Jobs, Skills, Training and Labour (2013–2016)': 'Jobs, Skills, Training and Labour (2013-2016)',
    'Aboriginal Relations': 'Aboriginal Relations (2008-2011, 2013-2016)',
    'AboriginalRelations': 'Aboriginal Relations (2008-2011, 2013-2016)',
    'Advanced Education and Technology (2006-2013)': 'Advanced Education and Technology (2006-2012)',
    'Seniors': 'Seniors (2001-2004, 2011-2013, 2014-2016)',
    'Seniors (2001–2004, 2011–2013, 2014–2016)': 'Seniors (2001-2004, 2011-2013, 2014-2016)',
    'Municipal AffairsandHousing(2006-2008)': 'Municipal Affairs and Housing (2006-2008)',
    'Justice (1992-1993, 2011-2013)': 'Justice (1992-1993, 2011-2012)',
    'International, Intergovernmental and Aboriginal Relations (2006-2008, 2011-2013)': 'International, Intergovernmental and Aboriginal Relations (2006-2008, 2011-2012)',
    'Public Works, Supply, and Services (1983-1999)': 'PublicWorks, Supply, and Services (1983-1999)',
    'Treasury Board and Enterprise (2011-2013)': 'Treasury Board and Enterprise (2011-2012)',
    'Treasury Board (2004-2006, 2008-2011, 2013-2014)': 'Treasury Board (2004-2011)',
    "Aboriginal Relations (2008–2011, 2013–2016)": 'Aboriginal Relations (2008-2011, 2013-2016)'
}

def change_pkg_dict_for_import_deployment(data_dict, mode):
    data_dict['url'] = ''
    if mode == 'create':
        data_dict['_ckan_phase'] = ''
    elif mode == 'update' and '_ckan_phase' in data_dict:
        del data_dict['_ckan_phase']

    if 'topic' in data_dict:
        if not data_dict['topic']: 
            data_dict['topics'] = ['environment']
        else:
            data_dict['topics'] = get_topics_name(data_dict['topic'])
        del data_dict['topic']

    if 'extras' in data_dict:
        for e in data_dict['extras']:
            if 'topic' == e['key']:
                e['key'] = 'topics'
                break
    if 'id' in data_dict and mode == 'create':
        del(data_dict['id'])
    elif not 'id' in data_dict and mode == 'update':
        data_dict['id'] = get_pkg_id(data_dict['name'])
    if 'groups' in data_dict:
        for ind, g in enumerate(data_dict['groups']):
            if g.has_key('id') and mode =='create':
                del(data_dict['groups'][ind]['id'])
            elif not g.has_key('id') and mode =='update':
                data_dict['groups'][ind]['id'] = get_group_id(g['name'], 'group')
    if 'tags' in data_dict:
        for ind, t in enumerate(data_dict['tags']):
            if t.has_key('id') and mode == 'create':
                del(data_dict['tags'][ind]['id'])
            elif not t.has_key('id') and mode == 'update':
                data_dict['tags'][ind]['id'] = get_tag_id(data_dict['tags'][ind]['name'])
    if 'revision_id' in data_dict:
        del(data_dict['revision_id'])
    if not 'organization' in data_dict or not data_dict['organization']:
        data_dict['organization'] = {'name': 'servicealberta'}
    if 'organization' in data_dict:
        if data_dict['organization'].has_key('name'):
            data_dict['organization']['name'] = data_dict['organization']['name'].encode('utf-8')
            if GROUP_NAME_MATCH.has_key(data_dict['organization']['name']):
                data_dict['organization']['name'] = GROUP_NAME_MATCH[data_dict['organization']['name']]
        if data_dict['organization'].has_key('id') and mode == 'create':
            del(data_dict['organization']['id'])
        elif not data_dict['organization'].has_key('id') and mode == 'update':
            data_dict['organization']['id'] = get_group_id(data_dict['organization']['name'], 'organization')
        if data_dict['organization'].has_key('revision_id'):
            del(data_dict['organization']['revision_id'])
    if not 'owner_org' in data_dict:
        data_dict['owner_org'] = ''
    if 'owner_org' in data_dict:
        try:
            data_dict['organization']['name']
        except KeyError:
            raise NotFound('Could not find organization name in dataset {0}'.format(data_dict['name']))
        else:
            data_dict['owner_org'] = data_dict['organization']['name']

    if 'resources' in data_dict:
        for r in data_dict['resources']:
            if r.has_key('id') and mode == 'create':
                del(r['id'])
            elif not r.has_key('id') and mode == 'update':
                r['id'] = get_resource_id(r, data_dict['id'])
            if r.has_key('package_id') and mode == 'create':
                del(r['package_id'])
            elif not r.has_key('package_id') and mode == 'update':
                r['package_id'] = data_dict['id']

            if r.has_key('url_type'):  # here will be added more to satisfy IDDP later. For the OGP 
                                       # data deployment, this field has to be empty
                r['url_type'] = ''
            if r.has_key('tracking_summary'):
                del(r['tracking_summary'])
            if not r.has_key('classification'):
                r['classification'] = 1

    if not 'process_state' in data_dict or data_dict['process_state'] == '':
        data_dict['process_state'] = 'Approved'
    if not 'reason' in data_dict or data_dict['reason'] == '':
        data_dict['reason'] = 'NA'
    if data_dict['process_state'] == 'Approved':
        data_dict['private'] = False
    data_dict['creator_user_id'] = toolkit.c.userobj.id

    if not 'date_created' in data_dict and 'date_modified' in data_dict:
        data_dict['date_created'] = data_dict['date_modified']
    elif 'date_created' in data_dict and not 'date_modified' in data_dict:
        data_dict['date_modified'] = data_dict['date_created']
    elif not 'date_created' in data_dict and not 'date_modified' in data_dict:
        data_dict['date_modified'] = data_dict['date_created'] = datetime.date.today()

    if not 'creator' in data_dict or not data_dict['creator']:
        if 'source_type' in data_dict and data_dict['source_type'] == 'geoimport' and \
           'organization' in data_dict and data_dict['organization']['name'] == 'albertaenergyregulator':
            data_dict['creator'] = ['Alberta Energy Regulator']
        else:
            data_dict['creator'] = ['Alberta Energy Regulator']
    else:
        tmp =[]
        for c in data_dict['creator']:
            c = c.encode('utf-8')
            if CREATOR_MATCH.has_key(c):
                c = CREATOR_MATCH[c]
            tmp.append(c)
        data_dict['creator'] = tmp

    if not 'contact_email' in data_dict or not data_dict['contact_email']:
        data_dict['contact_email'] = 'NA'

    if not 'contact' in data_dict or not data_dict['contact']:
        data_dict['contact'] = 'NA'

    if not 'updatefrequency' in data_dict or \
       not data_dict['updatefrequency']:
        data_dict['updatefrequency'] = 'Once'

    if not 'sensitivity' in data_dict or not data_dict['sensitivity']:
        data_dict['sensitivity'] = 'unrestricted'

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

def get_pkg_id(pkg_name):
    try:
        pkg_dict = toolkit.get_action('package_show')(data_dict={'id': pkg_name})
    except NotFound:
        print("Dataset '{0}' not found!".format(pkg_name))
        raise NotFound("Dataset '{0}' not found!".format(pkg_name))
    return pkg_dict['id']

def get_resource_id(resource, pkg_id):
    try:
        pkg_dict = toolkit.get_action('package_show')(data_dict={'id': pkg_id})
    except NotFound:
        print("Dataset '{0}' not found!".format(pkg_name))
        raise NotFound("Dataset '{0}' not found!".format(pkg_name))
    if len(pkg_dict['resources']) == 0:
        return ''
    for r in pkg_dict['resources']:
        if r['name'] == resource['name']:
            return r['id']
    return ''

def get_group_id(group_name, type):
    try:
        if type == 'group':
            group_dict = toolkit.get_action('group_show')(data_dict={'id': group_name})
        elif type == 'organization':
            group_dict = toolkit.get_action('organization_show')(data_dict={'id': group_name})
    except NotFound:
        print("'{0}' {1} not found!".format(type, group_name))
        raise NotFound("'{0}' {1} not found!".format(type, group_name))
    return group_dict['id']

def  get_tag_id(tag_name):
    try:
        tag_dict = toolkit.get_action('tag_show')(data_dict={'id': tag_name})
    except NotFound:
        print("Tag '{0}' not found!".format(tag_name))
        raise NotFound("Tag '{0}' not found!".format(tag_name))
    return tag_dict['id']

def get_topics_name(titles):
    if len(titles) == 0:
        return []
    if not isinstance(titles, list):
        titles = [titles]
    tmp = []
    gs = helpers.topics_available(permission='read')
    for t in titles:
        t = t.encode('utf-8')
        if TOPICS_NAME_MATCH.has_key(t):
            t = TOPICS_NAME_MATCH[t]
        flag = 0
        for g in gs:
            if g['label'] == t:
                tmp.append(g['value'])
                flag = 1
                break
        if flag == 0:
            raise NotFound("Could not find topics '{0}' in {1} in database group table.".format(t, ','.join(titles)))
    return tmp



        