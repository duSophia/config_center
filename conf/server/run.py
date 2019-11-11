import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(base_dir))

from conf.server.views import app
from conf.server import models

if __name__ == '__main__':
    models.init_schema()
    app.run(host='0.0.0.0', port=8888, debug=True)
