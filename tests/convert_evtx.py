from os.path import join, dirname, abspath
from evtx_miner import convert_evtx_directory
import logging

logging.basicConfig(level=logging.DEBUG)

SCRIPT_DIR = dirname(abspath(__file__))
INPUT_DIR = join(SCRIPT_DIR, 'samples', 'evtx')
OUTPUT_DIR = join(SCRIPT_DIR, 'output', 'evtx')


if __name__ == '__main__':
    convert_evtx_directory(INPUT_DIR, OUTPUT_DIR)

