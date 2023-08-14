import socket
import json
import http.server
import threading
import os
import pathlib
import urllib.parse
import mimetypes
from datetime import datetime


BASE_DIR = pathlib.Path()
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000


def send_data_to_socket(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(data, (SERVER_IP, SERVER_PORT))
    client_socket.close()

# Конфігурація HTTP сервера
class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        send_data_to_socket(data)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

def save_data(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        data_dict = {str(datetime.now()): {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}}

        with open(BASE_DIR.joinpath('storage/data.json'), 'r+', encoding='utf-8') as fd:
            try:
                data_file = json.load(fd)
            except:
                data_file = {}
            data_file.update(data_dict)
            fd.seek(0)
            json.dump(data_file, fd, ensure_ascii=False, indent=4)
            fd.truncate()
    except ValueError as err:
        print(f'{err}')
    except OSError as err:
        print(f'{err}')



# Конфігурація Socket сервера
def socket_server():
    HOST = '127.0.0.1'
    PORT = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))

    print("Сокет сервер прослуховує на порту", PORT)

    while True:
        data, addr = server_socket.recvfrom(1024)
        save_data(data)

        print("Дані збережено:")


def main():
    if not os.path.exists('storage'):
        os.makedirs('storage')
        with open('storage/data.json', 'w') as json_file:
            json.dump({}, json_file)

    http_thread = threading.Thread(target=run)
    socket_thread = threading.Thread(target=socket_server)

    http_thread.start()
    socket_thread.start()


def run(server_class=http.server.HTTPServer, handler_class=MyHTTPRequestHandler):
    server_address = ('0.0.0.0', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    main()