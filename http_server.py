import socket
import sys
import re
import os 

WWW_PATH = r"C:\Users\yonat\Documents\Yuval\devops\networking\http-server4.4\wwwroot"
SOCKET_TIMEOUT = 1
SWITCH_FILES  = {'\\index1.html': '\\index.html'}
FORBIDDEN = ['\\index3.html']

def check_request(request):
    return re.search("^(GET )((\/[a-zA-Z0-9\.]{0,}){1,})( HTTP\/[1-9\.]+)", request)

def create_response(path):
    path = path.replace('/', '\\')
    
    if path == '\\':
        path = '\\index.html'
    
    if not path.endswith(('.html', '.jpg', '.js', '.css', '.ico')):
        path = path + '.html'
    
    if path in FORBIDDEN:
        return "HTTP/1.1 403 Forbidden\r\n".encode()
    
    if path in SWITCH_FILES:
        return "HTTP/1.1 302 Found\r\nLocation: {}\r\n".format(SWITCH_FILES[path]).encode()
    
    try:
        file_type = path.split('.')[-1]
        if file_type == 'txt' or file_type == 'html':
            file_type = "text/html; charset=utf-8"
            file = open(WWW_PATH + path, 'r', encoding="utf8").read()
            return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n{}".format(os.path.getsize(WWW_PATH + path), file_type, file).encode()
        if file_type == 'js':
            file_type = "text/javascript; charset=utf-8"
            file_size = os.path.getsize(WWW_PATH + path)
            file = open(WWW_PATH + path, 'r', encoding="utf8").read()
            return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n{}".format(len(file), file_type, file).encode()
        if file_type == 'css':
            file_type = "text/css"
            file = open(WWW_PATH + path, 'r').read()
            return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n{}".format(os.path.getsize(WWW_PATH + path), file_type, file).encode()
        if file_type == 'jpg':
            file_type = "image/jpeg"
            image_path = WWW_PATH + path
            file = open(image_path, 'rb').read()
            return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n".format(os.path.getsize(WWW_PATH + path), file_type).encode() + file
        if file_type == 'ico':
            file_type = "image/x-image"
            image_path = WWW_PATH + path
            file = open(image_path, 'rb').read()
            return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n".format(os.path.getsize(WWW_PATH + path), file_type).encode() + file
        else:
            raise FileNotFoundError 
    except IsADirectoryError:
        return "HTTP/1.1 404 Not Found".encode()
    except FileNotFoundError as e:
        return "HTTP/1.1 404 Not Found".encode()
    except PermissionError:
        return "HTTP/1.1 404 Not Found".encode()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:        
        #create socket bound to port 80 and listen to connection
        server_socket.bind(('0.0.0.0', 80))
        server_socket.listen()
        print("Server is up and running")

        while True:
            (client_socket, client_address) = server_socket.accept()
            #client_socket.settimeout(SOCKET_TIMEOUT)
            
            request = client_socket.recv(1500).decode()
            end_line = request.index("\r\n")
            request = request[:end_line]
            
            if check_request(request):
                request_elements = request.split(' ')
                path = request_elements[1]
                response = create_response(path)
                client_socket.send(response)
            else:
                client_socket.send("HTTP/1.1 500 Internal Server Error".encode())
            
            client_socket.close()


if __name__ == "__main__":
    main()