import  ckanext.scheming.helpers as h

def _get_process_state_field():
	opendata_scheme = h.scheming_get_schema('dataset', 'opendata')
	fields = opendata_scheme['dataset_fields']
	return h.scheming_field_by_name(fields, "process_state")


def get_process_state_list_not_allow_incomplete():
	ps = _get_process_state_field()
	return ps['form_not_allow_incomplete_dataset']


def get_required_fields_name():
	opendata_scheme = h.scheming_get_schema('dataset', 'opendata')
	fields = opendata_scheme['dataset_fields']
	required_fields_name = []
	for f in fields:
		if f.get('required'):
			required_fields_name.append(f.get('field_name'))
	return  required_fields_name


def get_all_process_states():
	ps = _get_process_state_field()
	return [ c['value'] for c in ps['choices'] ]

