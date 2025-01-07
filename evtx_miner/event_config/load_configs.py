from .event_config import EventConfig
import json
from evtx_miner.config import COMPILED_CONFIGS_JSON
from ..titles_db import get_title

_event_configs = None


# DEFAULT_CONFIG = EventConfig(0, '', '')


def _get_event_configs():
    global _event_configs
    if _event_configs is None:
        with open(COMPILED_CONFIGS_JSON) as fin:
            data = json.load(fin)
        _event_configs = {(c['channel'], c['provider'], c['event_id']): EventConfig(**c) for c in data}
    return _event_configs


def get_event_config(channel, provider, event_id) -> EventConfig:
    _event_configs_db = _get_event_configs()
    if (channel, provider, event_id) not in _event_configs_db:
        # create a new event config
        _event_configs_db[(channel, provider, event_id)] = EventConfig(
            event_id, channel, provider,
            title=get_title(channel, provider, event_id)
        )
    return _event_configs_db[(channel, provider, event_id)]  # or DEFAULT_CONFIG
