from os.path import join, dirname, abspath
import yaml
import json
import os

PROJECT_DIR = dirname(dirname(abspath(__file__)))
CONFIGS_DIR = join(PROJECT_DIR, 'event_configs')
OUTPUT_PATH = join(PROJECT_DIR, 'evtx_miner', 'databases', 'compiled_configs.json')


def load_yaml(filepath):
    with open(filepath) as fin:
        return yaml.safe_load(fin)


def compile_configs(configs_dir=CONFIGS_DIR, output_path=OUTPUT_PATH):
    configs = [load_yaml(join(configs_dir, fn)) for fn in os.listdir(configs_dir) if
               fn.endswith('.yaml') and not fn.startswith('_')]
    with open(output_path, 'w') as fou:
        json.dump(configs, fou)


if __name__ == '__main__':
    compile_configs()
