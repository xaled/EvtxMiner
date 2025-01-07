from os.path import join, dirname, abspath
from evtx_miner import convert_xml_directory
import logging

logging.basicConfig(level=logging.DEBUG)

SCRIPT_DIR = dirname(abspath(__file__))
INPUT_DIR = join(SCRIPT_DIR, 'samples', 'xml')
OUTPUT_DIR = join(SCRIPT_DIR, 'output', 'xml')


if __name__ == '__main__':
    convert_xml_directory(INPUT_DIR, OUTPUT_DIR)
