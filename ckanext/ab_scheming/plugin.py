import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import json
from logic import validation
from helpers import get_pocess_list_not_allow_incomplete

class Ab_SchemingPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ab_scheming')
        
    def dataset_facets(self, facets_dict, package_type):
        facets_dict['dataset_type'] = plugins.toolkit._('Information Type')
        facets_dict['topic'] = plugins.toolkit._('Topics')
        facets_dict['audience'] = plugins.toolkit._('Audience')
        facets_dict['pubtype'] = plugins.toolkit._('Publication Type')
        return facets_dict
        
    def before_index(self, pkg_dict):
        if 'audience' in pkg_dict:
            pkg_dict['audience'] = json.loads(pkg_dict['audience'])
        if 'topic' in pkg_dict:
            pkg_dict['topic'] = json.loads(pkg_dict['topic'])
        if 'pubtype' in pkg_dict:
            pkg_dict['pubtype'] = json.loads(pkg_dict['pubtype'])
            
        return pkg_dict
    
    """
    IValidators
    """
    def get_validators(self):
        return {'ab_scheming_scheming_required': validation.scheming_required,
                'ab_scheming_resource_required': validation.resource_required}

    """
    ITemplateHelpers
    """
    def get_helpers(self):
        return {'ab_scheming_process_state_list_not_allow_incomplete': get_pocess_list_not_allow_incomplete}