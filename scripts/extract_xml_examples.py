import os
import re
from os.path import join, dirname, abspath, exists, isdir
from evtx import PyEvtxParser
from evtx_miner.convert import parse_evtx_xml, clean_xml
import logging
from lxml import etree as ET

logging.basicConfig(level=logging.DEBUG)
PROJECT_DIR = dirname(dirname(abspath(__file__)))
INPUT_DIR = join(PROJECT_DIR, 'tests', 'samples', 'evtx')
OUTPUT_DIR = join(PROJECT_DIR, 'tests', 'samples', 'xml', 'criteria')


def find_and_extract_xml_sample(filepath, criteria_func):
    print("Processing filepath:", filepath)
    parser = PyEvtxParser(filepath)
    for ix, record in enumerate(parser.records()):
        try:
            xml_str = record['data'][39:]
            obj = parse_evtx_xml(xml_str)
            if criteria_func(xml_str, obj):
                return xml_str, obj
        except Exception as e:
            logging.getLogger().warning(f"Error parsing record {ix=} {e=}! Skipping record.", exc_info=True)
    return None, None


def main(criteria_func, *input_paths, samples_count=3):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    found_count = 0

    input_paths = input_paths or (INPUT_DIR,)
    evtx_files = list()
    for input_path in input_paths:
        if isdir(input_path):
            evtx_files.extend(join(input_path, fn) for fn in os.listdir(input_path) if fn.lower().endswith('.evtx'))
        else:
            evtx_files.append(input_path)

    for filepath in evtx_files:
        xml_str, obj = find_and_extract_xml_sample(filepath, criteria_func)
        if xml_str:
            ix = 1
            channel, provider, event_id = obj['channel'], obj['provider'], obj['event_id']
            output_filepath = join(OUTPUT_DIR,
                                   f"{channel.replace('/', '-')}_{provider.replace('/', '-')}_{event_id}.{ix}.xml")
            while exists(output_filepath):
                ix += 1
                output_filepath = join(OUTPUT_DIR,
                                       f"{channel.replace('/', '-')}_{provider.replace('/', '-')}_{event_id}.{ix}.xml")

            print("output example to ", output_filepath)
            with open(output_filepath, 'w') as fou:
                fou.write(xml_str)

            found_count += 1

            if found_count >= samples_count:
                break


def event_id_criteria(channel, provider, event_id):
    def _criteria_func(xml_str, obj):
        if event_id == obj['event_id'] and channel == obj['channel'] and provider == obj['provider']:
            return True
        return False

    return _criteria_func


def task_content_criteria(xml_str, obj):
    return not not obj['data'].get('TaskContent')


def is_likely_xml(s):
    return s.strip().startswith("<") and re.search(r"</\w+>", s)


def embedded_xml(xml_str, obj):
    for v in obj['data'].values():
        if isinstance(v, str) and is_likely_xml(v):
            return True
    return False


def non_usual_data(xml_string, obj):
    root = ET.fromstring(clean_xml(xml_string))
    for data in root.xpath("/Event/EventData/Data"):
        if any(attr for attr in data.attrib if attr != "Name") or list(data):
            return True
    return False


if __name__ == '__main__':
    main(non_usual_data,)
