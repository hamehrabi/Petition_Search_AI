# config file - just some basic settings for the app
# I copied some of this from tutorials online

import os

# basic stuff for the API
API_TITLE = 'Petition Search'
HOST = '127.0.0.1'  # just running locally for now
PORT = 8000

# file paths - not sure if this is the best way but it works
import os.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'data', 'petitions.csv')
CACHE_FILE = os.path.join(BASE_DIR, 'data', 'embeddings_cache.pkl')

# AI model name - copied from documentation
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'

# search settings
MAX_RESULTS = 10  # how many results to show
