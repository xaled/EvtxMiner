from os.path import dirname, join, abspath

MODULE_PATH = dirname(abspath(__file__))
DATABASES_DIR = join(MODULE_PATH, 'databases')
TITLES_CSV = join(DATABASES_DIR, 'titles.csv')
COMPILED_CONFIGS_JSON = join(DATABASES_DIR, 'compiled_configs.json')
