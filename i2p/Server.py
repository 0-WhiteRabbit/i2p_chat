import socket
import ssl
import logging
import random


class Server:
    sock = None
    logger = None
    bind_pool: [[socket, str]] = []
    name: str = ''
    context = None

    def init(self, port):
        self.logger = logging.getLogger('main_logger')

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain('cert/key.crt', 'cert/key.key')
        self.context.verify_mode = ssl.CERT_NONE

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', port))
        self.sock.listen(10)
        self.sock.settimeout(5)

        self.name = str(random.randint(10000, 99999))
        self.logger.info(f'Server: success bind to {port}')

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Server, cls).__new__(cls)
        return cls.instance

    def close_all_connection(self):
        for i in self.bind_pool:
            i[0].close()
        self.bind_pool = []
        self.logger.info(f'Server: close all connection success')
