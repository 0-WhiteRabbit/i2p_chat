#!venv/bin/python

import logging
import sys

from app import app
from i2p.Server import Server
from i2p.NetConnect import NetConnect
from i2p.crypto import gen_ssl_cert

if len(sys.argv) != 4:
    print(f"Use {sys.argv[0]} log_file port_to_listen")
    sys.exit(1)

logger = logging.getLogger('main_logger')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(sys.argv[1])
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)
logger.info('start'.center(50, '-'))

gen_ssl_cert('*')

server_worker = Server()
server_worker.init(int(sys.argv[2]))
connect_worker = NetConnect()
connect_worker.init(server_worker.name)


app.run(debug=False, port=int(sys.argv[3]), use_reloader=False)
