from .actions import level_mapping
from .value import Value
from ..xml_to_dict import xml_to_dict_ex1, embedded_xml_to_dict, is_likely_xml
import logging
from evtx_miner.xpath import xpath

logger = logging.getLogger(__name__)


class _EventConfigDataProcessing:
    __slots__ = 'key_prefix', 'type', 'split_separator', 'binary', 'extract_title'

    def __init__(self, key_prefix='payload', split_separator='\n\r', binary=None, extract_title=False, **kwargs):
        # default data processing options:
        # self.data_processing.setdefault('key_prefix', 'payload')
        # self.data_processing.setdefault('type', 'auto')  # split, auto, only_values
        # self.data_processing.setdefault('split_separator', '\n\r')
        # # config['data_processing'].setdefault('binary', None) # TODO
        # # self.data_processing.setdefault('extract_title', None)  # auto
        self.key_prefix = key_prefix
        self.split_separator = split_separator
        self.type = kwargs.get('type', 'auto')  # split, auto, only_values
        self.binary = binary  # TODO
        self.extract_title = extract_title
        # TODO auto search for separator


class EventConfig:
    __slots__ = 'author', 'description', 'title', 'event_id', 'channel', 'provider', 'event_type', 'data_processing', \
                'values', 'references'

    def __init__(self, event_id: int, channel: str, provider: str, author: str = None, description: str = None,
                 title: str = None, event_type: str = None, data_processing: dict = None, values: list[dict] = None,
                 references: list[str] = None, **kwargs):
        self.event_id = event_id
        self.channel = channel
        self.provider = provider
        self.author = author
        self.description = description
        self.title = title
        self.event_type = event_type
        self.values: list[Value] = [Value(**value) for value in values or list()]
        self.references = references
        self.data_processing: _EventConfigDataProcessing = _EventConfigDataProcessing(**(data_processing or {}))

    def process_evtx_record(self, record_xml_tree):
        def _extract_values(_dt):
            to_delete = []
            normalized_dict = {}
            for value_config in self.values:
                value_config.extract_value(record_xml_tree, _dt, to_delete, normalized_dict)

            return _dt, to_delete, normalized_dict

        def _extract_event_data(_event_data_element):
            title = None
            dp_config = self.data_processing
            event_data_dict = dict()
            event_data_list = list()
            # first_value = None
            for ix, child in enumerate(_event_data_element):
                # print(ix, child)
                is_data = child.tag.lower() == 'data'
                value = child.text.strip() if child.text is not None else None
                # TODO Unusual data tags: (with attributes other than Name or children) did not find any

                # Embedded XML
                if value and is_likely_xml(value):
                    value = embedded_xml_to_dict(value)

                # if first_value is None and is_data:
                #     first_value = value

                key = child.attrib.get('Name', None)
                if key or not is_data:
                    event_data_dict[key or child.tag.lower()] = value
                else:
                    event_data_list.append(value or "")

            # split multi line data items
            split = dp_config.type == 'split' or (dp_config.type == 'auto' and len(event_data_list) == 1)
            key_prefix = dp_config.key_prefix
            if split:
                parts = [
                    p.strip() for itm in event_data_list for p in itm.split(dp_config.split_separator)
                ]
                event_data_dict.update({f"{key_prefix}{ix}": p for ix, p in enumerate(parts)})
                if dp_config.extract_title:
                    title = event_data_dict.get(f'{key_prefix}0', None)
            elif event_data_list:
                event_data_dict.update({f"{key_prefix}{ix}": p for ix, p in enumerate(event_data_list)})
                if dp_config.extract_title:
                    title = event_data_list[0].split(dp_config.split_separator)[0].strip()

            # pprint(event_data_dict)
            title = title[:75] if title is not None else None
            return event_data_dict, title

        def _get_event_data():
            data_dict = {}
            title = None

            if self.data_processing.type != 'only_values':
                _event_data_element = record_xml_tree.xpath('/Event/EventData')
                _event_data_element = _event_data_element[0] if _event_data_element else None

                # extract data items
                if _event_data_element is not None:
                    event_data_dict, title = _extract_event_data(_event_data_element)
                    data_dict.update(event_data_dict)

                # Other data: UserData, etc...
                for child in record_xml_tree:
                    if child.tag.lower() not in ('system', 'eventdata'):
                        data_dict.update(xml_to_dict_ex1(child))

            data_dict, to_delete, normalized_dict = _extract_values(data_dict)

            # Remove temps
            data_dict = {_k: _v for _k, _v in data_dict.items() if _k not in to_delete}

            return data_dict, normalized_dict, title

        # channel = xpath(record_xml_tree, '/Event/System/Channel')
        # provider = xpath(record_xml_tree, '/Event/System/Provider/@Name')
        # event_id = xpath(record_xml_tree, '/Event/System/EventID', cast=int)

        event_data, normalized_fields, event_data_title = _get_event_data()

        parsed_data = {
            'timestamp': xpath(record_xml_tree, '/Event/System/TimeCreated/@SystemTime'),
            'channel': self.channel,
            'provider': self.provider,
            'event_id': self.event_id,
            'event_id_qualifier': xpath(record_xml_tree, '/Event/System/EventID/@Qualifiers', cast=int),
            'level': level_mapping.get_mapping(xpath(record_xml_tree, '/Event/System/Level', cast=int)),
            'opcode': xpath(record_xml_tree, '/Event/System/Opcode', cast=int),  # opcode mappings?
            'task': xpath(record_xml_tree, '/Event/System/Task', cast=int),  # task mappings?
            'keywords': extract_keywords(xpath(record_xml_tree, '/Event/System/Keywords', )),
            'event_record_id': xpath(record_xml_tree, '/Event/System/EventRecordID', cast=int),
            'computer': xpath(record_xml_tree, '/Event/System/Computer'),
            'security': xpath(record_xml_tree, '/Event/System/Security'),
            'activity_id': xpath(record_xml_tree, '/Event/System/Correlation/@ActivityID'),
            'data': event_data,
            'title': self.title or event_data_title,
        }

        # add normalized fields
        for k, v in normalized_fields.items():
            if k not in parsed_data:
                parsed_data[k] = v
            else:
                logger.warning(f"Skipping a normalized field key that overwrite a main field: {k=} {self.event_id=}")

        return parsed_data


NAMED_KEYWORDS = {
    0x0000000000010000: 'Shell',
    0x0000000000020000: 'Properties',
    0x0000000000040000: 'FileClassStoreAndIconCache',
    0x0000000000080000: 'Controls',
    0x0000000000100000: 'APICalls',
    0x0000000000200000: 'InternetExplorer',
    0x0000000000400000: 'ShutdownUX',
    0x0000000000800000: 'CopyEngine',
    0x0000000001000000: 'Tasks',
    0x0000000002000000: 'WDI',
    0x0000000004000000: 'StartupPerf',
    0x0000000008000000: 'StructuredQuery',
    0x0001000000000000: 'win:Reserved',
    0x0002000000000000: 'win:WDIContext',
    0x0004000000000000: 'win:WDIDiag',
    0x0008000000000000: 'win:SQM',
    0x0010000000000000: 'win:AuditFailure',
    0x0020000000000000: 'win:AuditSuccess',
    0x0040000000000000: 'win:CorrelationHint',
    0x0080000000000000: 'win:EventlogClassic',
    0x0100000000000000: 'win:ReservedKeyword56',
    0x0200000000000000: 'win:ReservedKeyword57',
    0x0400000000000000: 'win:ReservedKeyword58',
    0x0800000000000000: 'win:ReservedKeyword59',
    0x1000000000000000: 'win:ReservedKeyword60',
    0x2000000000000000: 'win:ReservedKeyword61',
    0x4000000000000000: 'win:ReservedKeyword62',
    0x8000000000000000: 'Microsoft-Windows-Shell-Core/Diagnostic',
}


def extract_keywords(hex_string):
    # Convert the hex string to an integer
    if not hex_string:
        return []

    try:
        value = int(hex_string, 16)
    except ValueError:
        return [hex_string]

    flags = []

    # Check each bit position and add the corresponding flag
    i = 0
    while value:
        bit_value = 1 << i
        if value & 1:
            flags.append(NAMED_KEYWORDS.get(bit_value, f"keyword{i}"))
        i += 1
        value = value >> 1

    return flags
