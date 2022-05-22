import ssl
from urllib.parse import ParseResult
import socket

from i2p.message_code import GET_NAME, MY_NAME, PING, pars_init_conn_name


class Connect:
    addr = None
    name = ''

    def __init__(self):
        self.def_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.def_sock.settimeout(5)
        self.sock = None

    def client_connect(self,  url: ParseResult, names):
        context = ssl.create_default_context()
        context.check_hostname = 0
        context.verify_mode = ssl.CERT_NONE
        if self.def_sock is None:
            self.def_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.def_sock.settimeout(5)
        try:
            self.def_sock.connect((url.hostname, url.port))
            self.sock = context.wrap_socket(self.def_sock, server_hostname=url.hostname)
            self.addr = url
            self.sock.send(GET_NAME)
            ans = self.sock.recv(1024)
            code, res = pars_init_conn_name(ans)
            if code:
                self.name = res[0]
                k = bytes('\n'.encode()).join(names)
                self.sock.send(MY_NAME + str(len(names)).encode() + '\n'.encode() + k)
                return res
            else:
                self.sock.close()
        except ConnectionRefusedError:
            if not (self.sock is None):
                self.sock.close()
            self.def_sock.close()
        except socket.timeout:
            self.def_sock.close()
        return []

    def server_connect(self,  sock: socket.socket, names, context):
        b_sock = None
        try:
            b_sock, _ = sock.accept()
            self.sock = context.wrap_socket(b_sock, server_side=True)
            ans = self.sock.recv(1024)
            if ans == GET_NAME:
                k = bytes('\n'.encode()).join(names)
                self.sock.send(MY_NAME + str(len(names)).encode() + '\n'.encode() + k + '\n'.encode())
                ans = self.sock.recv(1024)
                code, res = pars_init_conn_name(ans)
                if code:
                    self.name = res[0]
                    return res
                else:
                    self.sock.close()
            else:
                self.sock.close()
        except socket.timeout:
            if not (b_sock is None):
                b_sock.close()
        return []

    def ping(self):
        self.sock.send(PING)
        return 1

    def send(self, msg: str):
        self.sock.send(msg.encode())
        return 1

    def send_byte(self, msg: bytes):
        self.sock.send(msg)
        return 1

    def get_name(self):
        return self.name

    def close_connection(self):
        self.sock.close()

    def get_information(self):
        return self.sock.recv(2048).replace(PING, b'')
