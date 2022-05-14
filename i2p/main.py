from select import select
from urllib.parse import urlparse
import sys
import logging

from NetConnect import NetConnect
from Server import Server
import crypto

MAIN_LOG_FILE_NAME = 'log.log'

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Use {sys.argv[0]} log_file port_to_listen")
        sys.exit(1)

    logger = logging.getLogger('main_logger')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(sys.argv[1])
    handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
    logger.addHandler(handler)
    logger.info('start'.center(50, '-'))

    crypto.gen_ssl_cert('*')

    server_worker = Server()
    server_worker.init(int(sys.argv[2]))
    connect_worker = NetConnect(server_worker.name)

    rlist = 1
    try:
        while True:
            if rlist:
                print('Your command: ', end='')
                sys.stdout.flush()
            rlist, _, _ = select([sys.stdin], [], [], 0.3)
            if rlist:
                command = sys.stdin.readline().strip()
                if len(command) > 0:
                    if command == '0':
                        connect_worker.close_all_connection()
                        sys.exit()
                    elif command == 'list':
                        print((b'\n'.join(connect_worker.get_all_connect())).decode())
                    elif 'conn' in command[0:5]:
                        url = urlparse(command.split(' ')[1])
                        if connect_worker.init_connect(url):
                            print("Connect successes!")
                        else:
                            print("Connection failed!")
                    elif 'help' in command[0:5]:
                        print('''connect to another user:
                                Your command: conn i2p://127.0.0.1:8000
                                send: send test
                                exit: 0''')
                    elif 'send' in command[0:5]:
                        name, mes = command.strip().split(' ')[1:]
                        connect_worker.send(name, mes)
                elif len(command) > 0:
                    connect_worker.try_send(command)
            connect_worker.init_bind_connect(server_worker.sock, server_worker.context)
            connect_worker.check_message()
    except KeyboardInterrupt:
        connect_worker.close_all_connection()
        sys.exit()
