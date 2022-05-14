import socket
from urllib.parse import ParseResult
import logging

from i2p.Connect import Connect
from i2p.message_code import NEW, pars_new_name, MESS


class NetConnect:
    net_name = set()
    connect_pool: [Connect] = []
    logger = None
    name: str = ''
    mes = ''

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NetConnect, cls).__new__(cls)
        return cls.instance

    def init(self, name: str):
        self.name = name
        self.net_name.add(name.encode())
        self.logger = logging.getLogger('main_logger')

    def init_connect(self, url: ParseResult):
        for i in self.connect_pool:
            if i.addr == url:
                return
        conn = Connect()
        name = conn.client_connect(url, self.net_name)
        if conn.sock is not None and conn.sock.fileno() != -1:
            new = []
            for i in name:
                n = len(self.net_name)
                self.net_name.add(i)
                if len(self.net_name) > n:
                    new.append(i)
            if new:
                self.send_new_names(new)
            self.connect_pool.append(conn)
            self.logger.info(f'Client: connection success')
            return 1
        else:
            self.logger.info(f'Client: connection failed')
            return 0

    def init_bind_connect(self, sock: socket.socket, context):
        conn = Connect()
        name = conn.server_connect(sock, self.net_name, context)
        if conn.sock is not None and conn.sock.fileno() != -1:
            self.connect_pool.append(conn)
            for i in name:
                self.net_name.add(i)
            self.logger.info(f"You connected with {str(conn.name)}")
            self.mes += f"\nYou connected with {str(conn.name)}"
            return 1
        else:
            return 0

    def send_new_names(self, names: [bytes]):
        k = NEW + str(len(names)).encode() + '\n'.encode().join(names) + '\n'.encode()
        for i in self.connect_pool:
            i.send_byte(k)

    def try_send(self, msg: str):
        result = 0
        for i in self.connect_pool:
            if i.send(msg) != 0:
                result = 1
        if result > 0:
            self.logger.info(f'Client: success send msg')
        else:
            self.logger.info(f'Client: error send msg')
        return result

    def get_all_connect(self):
        return self.net_name

    def close_all_connection(self):
        for i in self.connect_pool:
            i.close_connection()
        self.connect_pool = []
        self.logger.info(f'Client: close all connection success')

    def check_message(self):
        for conn in range(len(self.connect_pool)):
            try:
                self.connect_pool[conn].ping()
                data = self.connect_pool[conn].get_information()
                if len(data):
                    if NEW in data:
                        code, names = pars_new_name(data[data.decode().find(str(NEW)):])
                        if code:
                            self.send_new_names(names)
                    elif MESS.encode() in data:
                        data1 = data.decode()
                        rec = data1[data1.find(MESS):].split('\n')[1]
                        if self.name == rec:
                            self.mes += '\nYou receive message: ' + data1[data1.find(MESS):].split('\n')[2]
                        else:
                            self.send(data1[data1.find(MESS):].split('\n')[1], data1[data1.find(MESS):].split('\n')[2],
                                      self.connect_pool[conn].name)
            except ConnectionResetError:
                logging.info(f'Server: connection with {self.connect_pool[conn]} close.')
                self.connect_pool.pop(conn)
            except BrokenPipeError:
                logging.info(f'Server: connection with {self.connect_pool[conn]} close.')
                self.connect_pool[conn].close_connection()
                self.connect_pool.pop(conn)
            except TimeoutError:
                logging.info(f'Server: connection with {self.connect_pool[conn]} close.')
                self.connect_pool[conn].close_connection()
                self.connect_pool.pop(conn)

    def send(self, name: str, mes: str, ex_from=""):
        k = MESS + '\n' + name + '\n' + mes + '\n'
        if name.encode() in self.net_name:
            for i in self.connect_pool:
                if i.name != ex_from:
                    i.send(k)
        else:
            self.mes += '\nHost not found in net!'
