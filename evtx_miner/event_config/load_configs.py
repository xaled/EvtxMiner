from .event_config import EventConfig
import json
from evtx_miner.config import COMPILED_CONFIGS_JSON

_event_configs = None
DEFAULT_CONFIG = EventConfig(0, '', '')


def _get_event_configs():
    global _event_configs
    if _event_configs is None:
        with open(COMPILED_CONFIGS_JSON) as fin:
            data = json.load(fin)
        _event_configs = {(c['channel'], c['provider'], c['event_id']): EventConfig(**c) for c in data}
    return _event_configs


def get_event_config(channel, provider, event_id) -> EventConfig:
    return _get_event_configs().get((channel, provider, event_id), None) or DEFAULT_CONFIG
