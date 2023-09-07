import http.server
import socketserver
import os

PORT = 8000

def start(path):
    os.chdir(path)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print("serving at port", PORT)
    httpd.serve_forever()

def stop(ser):
    ser.shutdown()