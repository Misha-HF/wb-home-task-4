from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import json
from threading import Thread
from datetime import datetime
import os
import mimetypes

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/message.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('message.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path.startswith('/static/'):
            self.send_static()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('error.html', 'rb') as file:
                self.wfile.write(file.read())


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



    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        post_data = post_data.split('&')
        username = post_data[0].split('=')[1]
        message = post_data[1].split('=')[1]
        send_to_socket(username, message)
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()

def send_to_socket(username, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    data = {'username': username, 'message': message}
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(json.dumps(data).encode(), ('localhost', 5000))

def socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('localhost', 5000))
        while True:
            data, addr = s.recvfrom(1024)
            save_to_json(data)

def save_to_json(data):
    data = json.loads(data.decode())
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    with open('storage/data.json', 'a') as file:
        json.dump({timestamp: data}, file, indent=4)
        file.write('\n')

def start_http_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    # Start socket server in a separate thread
    socket_thread = Thread(target=socket_server)
    socket_thread.start()

    # Start HTTP server
    start_http_server()
