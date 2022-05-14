import socket

PING = b'$p'
GET_NAME = b'$GetName'
MY_NAME = b'$name'
NEW = b'$new'
MESS = '$mes'


'''
INIT CONNECT:
1: $GetName
2: $name2\n12490\n14634\n
1: $name1\n21849\n

NEW HOSTS
1: $new2\n12347\n12345\n

MESS:
1: $mes\n12345\nblablabla\n
'''


def pars_init_conn_name(mes: bytes):
    try:
        if MY_NAME == mes[:len(MY_NAME)]:
            n = int(mes[len(MY_NAME):mes.find(bytes('\n'.encode()))])
            name = mes.split(bytes('\n'.encode()))[1:n+1]
            return 1, name
        return 0, []
    except Exception:
        return 0, []


def pars_new_name(mes: bytes):
    try:
        if NEW == mes[:len(NEW)]:
            n = int(mes[len(NEW):mes.find(bytes('\n'.encode()))])
            name = mes.split(bytes('\n'.encode()))[1:n+1]
            return 1, name
        return 0, []
    except Exception:
        return 0, []
