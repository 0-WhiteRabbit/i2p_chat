import sys
from urllib.parse import urlparse

import flask
from flask import render_template, redirect, request, Response
from app import app
from app.forms import Command
from time import sleep
from i2p.NetConnect import NetConnect
from i2p.Server import Server


@app.errorhandler(404)
def not_found(e):
    return redirect('/index')


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/content')
def content():
    def cheker():
        mes = ''
        mes1 = ''
        worker = NetConnect()
        server_worker = Server()
        while True:
            sleep(1)
            if mes != mes1:
                yield mes[len(mes1):]
            mes1 = mes
            worker.check_message()
            worker.init_bind_connect(server_worker.sock, server_worker.context)
            mes = worker.mes

    return Response(cheker(), mimetype='text/css')


@app.route('/', methods=['POST'])
@app.route('/index', methods=['POST'])
def command():
    if request.method == 'POST':
        command = str(request.form['comm'])
        connect_worker = NetConnect()
        if command == '0':
            connect_worker.close_all_connection()
            sys.exit()
        elif command == 'list':
            connect_worker.mes += (b'\n'.join(connect_worker.get_all_connect())).decode() + '\n'
        elif 'conn' in command[0:5]:
            url = urlparse(command.split(' ')[1])
            if connect_worker.init_connect(url):
                connect_worker.mes += "Connect successes!\n"
            else:
                connect_worker.mes += "Connection failed!\n"
        elif 'help' in command[0:5]:
            print('''connect to another user:
                    Your command: conn i2p://127.0.0.1:8000
                    send: send test
                    exit: 0''')
        elif 'send' in command[0:5]:
            name = command.strip().split(' ')[1]
            mes = ' '.join(command.strip().split(' ')[2:])
            connect_worker.send(name, mes)

    return render_template('index.html',
                           title='Sign In')

