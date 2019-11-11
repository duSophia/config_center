import logging
import os

SECRET_KEY = 'sfwkf#$dfkJKHF1fsdfk(#*$dK'

REDIS_CONF = dict(
    host='localhost',
    port='6379'
)

base_dir = os.path.dirname(os.path.abspath(__file__))
log_handler = logging.FileHandler(os.path.join(base_dir, 'conf.log'), encoding='utf8')
formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(handlers=[log_handler, logging.StreamHandler()], level=logging.INFO)

sqlchemy_db = dict(
    # charset='utf8mb4',
    drivername='mysql+mysqlconnector',
    host='localhost',
    username='root',
    password='P@55word',
    database='conf',
)

try:
    from .env_settings import *
except ImportError:
    pass
