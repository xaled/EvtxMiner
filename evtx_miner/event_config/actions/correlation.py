from abc import ABC, abstractmethod
from datetime import datetime

_correlation_configs = dict()
_search_fields_configs = dict()


class Correlation:
    __slots__ = 'key', 'search_fields', 'uuid', 'enrich_fields', 'normalized'

    def __init__(self, value_name, search_fields, enrich_fields, uuid=True, normalized=False, key=None, **kwargs):
        self.key = key or value_name
        self.search_fields: list[str] = search_fields
        self.enrich_fields: list[str] = enrich_fields
        self.uuid = uuid
        self.normalized = normalized

    def process_item(self, correlation_id, timestamp, extracted_data, normalized_dict):
        # init correlation db if not init
        config: _CorrelationConfig = self.get_config()
        source_data = normalized_dict if self.normalized else extracted_data
        enrich_data = {k: source_data.get(k, None) for k in self.enrich_fields}
        config.add_entry(correlation_id, timestamp, enrich_data)

    def get_config(self):
        # init
        if self.key not in _correlation_configs:
            _correlation_configs[self.key] = ExactCorrelationConfig(self.normalized) if self.uuid \
                else ExactTemporalCorrelationConfig(self.normalized)
            for field in self.search_fields:
                # if field not in _search_fields_configs:
                #     _search_fields_configs[field] = list()
                # _search_fields_configs[field].append(_correlation_configs[self.key])
                _search_fields_configs[field] = _correlation_configs[self.key]

        return _correlation_configs[self.key]


class CorrelationEntry:
    __slots__ = 'timestamp', 'data',

    def __init__(self, timestamp, data):
        self.timestamp: int = timestamp
        self.data: dict = data


class _CorrelationConfig(ABC):
    __slots__ = 'normalized', 'data'

    def __init__(self, normalized):
        self.normalized = normalized
        self.data: dict[str, CorrelationEntry | list[CorrelationEntry]] = dict()

    @abstractmethod
    def add_entry(self, correlation_id, timestamp, data):
        pass

    @abstractmethod
    def search_entry(self, correlation_id, timestamp) -> CorrelationEntry | None:
        pass


class ExactCorrelationConfig(_CorrelationConfig):
    def add_entry(self, correlation_id, timestamp, data):
        # TODO warning: duplicate correlation id
        self.data[correlation_id] = CorrelationEntry(None, data)

    def search_entry(self, correlation_id, timestamp) -> dict | None:
        if correlation_id in self.data:
            return self.data[correlation_id].data
        return None


class ExactTemporalCorrelationConfig(_CorrelationConfig):
    def add_entry(self, correlation_id, timestamp, data):
        timestamp = parse_timestamp(timestamp)
        if correlation_id not in self.data:
            self.data[correlation_id] = list()
        self.data[correlation_id].append(CorrelationEntry(timestamp, data))

    def search_entry(self, correlation_id, timestamp) -> dict | None:
        timestamp = parse_timestamp(timestamp)
        if correlation_id in self.data:
            return find_closest_entry(timestamp, self.data[correlation_id]).data
        return None


def parse_timestamp(timestamp):
    if not timestamp or not timestamp.strip():
        return 0
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    epoch_time = int(dt.timestamp())

    return epoch_time


def find_closest_entry(timestamp: int, entries: list[CorrelationEntry]) -> CorrelationEntry:
    # Initialize the closest entry as the first one
    closest_entry = entries[0]
    min_difference = abs(closest_entry.timestamp - timestamp)

    # Iterate through the entries to find the closest one
    for entry in entries[1:]:
        difference = abs(entry.timestamp - timestamp)
        if difference < min_difference:
            closest_entry = entry
            min_difference = difference

    return closest_entry


def find_correlation_data(correlation_key, correlation_id, timestamp):
    if correlation_key in _search_fields_configs:
        config: _CorrelationConfig = _search_fields_configs[correlation_key]
        enrich_data = config.search_entry(correlation_id, timestamp)
        if enrich_data:
            return enrich_data, config.normalized
    return None, None
