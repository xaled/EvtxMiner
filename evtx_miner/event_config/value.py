from .actions import *
from ..xpath import xpath


class Value:
    __slots__ = 'name', 'rename', 'key', 'extract', 'format', 'refine', 'value_mapping', 'normalized_key', \
                'temporary', 'options', 'correlation'

    def __init__(self, name: str, rename: str = None, key: str = None, extract=None, refine=None,
                 value_mapping=None, normalized_key: str = None, temporary: bool = None, correlation: dict = None,
                 **kwargs):
        self.name = name
        self.rename = rename
        self.key = key
        self.extract: Extract = Extract(extract) if extract else None
        self.format = kwargs.get('format')
        self.refine: Refine = Refine(refine) if refine else None
        self.value_mapping: Mapping = Mapping(value_mapping) if value_mapping else None
        self.normalized_key = normalized_key
        self.temporary = temporary if temporary is not None else self.name.startswith('_')
        self.options = kwargs.get('options')
        self.correlation: Correlation = Correlation(name, **correlation) if correlation else None

    def extract_value(self, record_xml_tree, extracted_data, to_delete, normalized_dict, timestamp):
        if self.temporary:
            to_delete.append(self.name)

        if self.rename:
            extracted_data[self.name] = extracted_data[self.rename]
            to_delete.append(self.rename)

        if self.key:
            extracted_data[self.name] = extracted_data[self.key]

        if self.extract:
            extracted_data[self.name] = xpath(record_xml_tree, self.extract.xpath,
                                              cast=self.extract.cast)

        if self.format:
            extracted_data[self.name] = self.format.format(**extracted_data)

        if self.refine:
            extracted_data[self.name] = self.refine.refine(extracted_data.get(self.name))

        if self.options:
            extracted_data[self.name] = find_options_value(extracted_data, self.name, *self.options)

        if self.value_mapping:
            extracted_data[self.name] = self.value_mapping.get_mapping(extracted_data.get(self.name))

        if self.normalized_key:
            normalized_dict[self.normalized_key] = extracted_data.get(self.name)

        if self.correlation:
            self.correlation.process_item(extracted_data[self.name], timestamp, extracted_data, normalized_dict)
