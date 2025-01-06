import json
from os import listdir, makedirs
from os.path import join, basename, dirname
import re

from evtx import PyEvtxParser
from lxml import etree as ET
from .event_config import get_event_config
from .xpath import xpath
import logging

logger = logging.getLogger(__name__)


def convert_evtx_directory(input_dir, output_dir):
    for fn in listdir(input_dir):
        if fn.lower().endswith('.evtx'):
            filepath = join(input_dir, fn)
            dst_path = join(output_dir, fn + '.jsonl')
            convert_evtx_file(filepath, dst_path)


def convert_evtx_file(filepath, dst_path):
    logger.info(f"Converting Evtx file to Jsonl {filepath=} {dst_path=}...")
    makedirs(dirname(dst_path), exist_ok=True)

    with open(dst_path, 'w') as fou:
        for record in parse_evtx_file(filepath):
            fou.write(json.dumps(record))
            fou.write('\n')


def parse_evtx_file(filepath):
    parser = PyEvtxParser(filepath)
    evtx_filename = basename(filepath)
    for ix, record in enumerate(parser.records()):
        try:
            xml_str = record['data'][39:]
            xml_str = re.sub(' xmlns="[^"]+"', '', xml_str)
            obj = parse_evtx_xml(xml_str)
            obj['evtx_filename'] = evtx_filename
            yield obj
        except Exception as e:
            logger.warning(f"Error parsing record {ix=} {e=}! Skipping record.")


def parse_evtx_xml(xml_string):
    tree = ET.fromstring(xml_string)

    channel = xpath(tree, '/Event/System/Channel')
    provider = xpath(tree, '/Event/System/Provider/@Name')
    event_id = xpath(tree, '/Event/System/EventID', cast=int)

    event_config = get_event_config(channel, provider, event_id)

    return event_config.process_evtx_record(tree)
