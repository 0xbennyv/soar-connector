# Define the application directory
import os

# Statement for enabling the development environment
DEBUG = False

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'soarconnector.db')
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "a;fgkn;alfkmg;lakfm;lkamfdhb;lksgnb;kls mg;nljkhaskmas;df,"

# Secret key for signing cookies
SECRET_KEY = "adlkgmpioquht6o98u231n45ykjhg naelgigtlow mhb';awmltehpjoiktnwlkhs;lkfmb;gnhdfo"

# Default Action with JSON sorting
JSON_SORT_KEYS=False

# Redis Server Config
REDIS_URL = os.getenv('REDIS_URL') or 'redis://'
RQ_QUEUES = ['xg-soar-ondemand', 'xg-soar-fw', 'xg-soar-fw-del', 'xg-soar-ip', \
            'xg-soar-ip-del', 'xg-soar-fqdn', 'xg-soar-fqdn-del',]
