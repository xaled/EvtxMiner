from .actions import *
from ..xpath import xpath


class Value:
    __slots__ = 'name', 'rename', 'key', 'extract', 'format', 'refine', 'value_mapping', 'normalized_key', 'temporary'

    def __init__(self, name: str, rename: str = None, key: str = None, extract=None, format_: str = None, refine=None,
                 value_mapping=None, normalized_key: str = None, temporary: bool = None):
        self.name = name
        self.rename = rename
        self.key = key
        self.extract: Extract = Extract(extract) if extract else None
        self.format = format_
        self.refine: Refine = Refine(refine) if refine else None
        self.value_mapping: Mapping = Mapping(value_mapping) if value_mapping else None
        self.normalized_key = normalized_key
        self.temporary = temporary if temporary is not None else self.name.startswith('_')

    def extract_value(self, record_xml_tree, extracted_data, to_delete, normalized_dict):
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

        if self.value_mapping:
            extracted_data[self.name] = self.value_mapping.get_mapping(extracted_data.get(self.name))

        if self.normalized_key:
            normalized_dict[self.normalized_key] = extracted_data.get(self.name)
