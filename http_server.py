import socket
import re
import os 

WWW_PATH = r"C:\Users\yonat\Documents\Yuval\devops\networking\http-server4.4\wwwroot"
SOCKET_TIMEOUT = 1
REDIRECT  = {'\\index1.html': '\\index.html'}
FORBIDDEN = {'\\index3.html'}

def check_request(request):
    if  re.search("^(GET )((\/[a-zA-Z0-9\.]{0,}){1,})( HTTP\/[1-9\.]+)", request):
        return True, request.split(' ')[1]
    return False, None

def file_data(path):
    file_type = path.split('.')[-1]
    if file_type == 'txt' or file_type == 'html':
        file_type = "text/html; charset=utf-8"
        with open(WWW_PATH + path, 'r', encoding="utf8") as file:
            file_content = file.read()
        return file_content, file_type, os.path.getsize(WWW_PATH + path)
    if file_type == 'js':
        file_type = "text/javascript; charset=utf-8"
        with open(WWW_PATH + path, 'r', encoding="utf8") as file:
            file_content = file.read()
        return file_content, file_type, len(file_content)
    if file_type == 'css':
        file_type = "text/css"
        with open(WWW_PATH + path, 'r') as file:
            file_content = file.read()
        return file_content, file_type, os.path.getsize(WWW_PATH + path)
    if file_type == 'jpg':
        file_type = "image/jpeg"
        with  open(WWW_PATH + path, 'rb') as file:
            file_content = file.read()
        return  file_content, file_type, os.path.getsize(WWW_PATH + path)
    if file_type == 'ico':
        file_type = "image/x-image"
        with open(WWW_PATH + path, 'rb') as file:
            file_content = file.read()
        return file_content, file_type, os.path.getsize(WWW_PATH + path)
    else:
        raise FileNotFoundError 

def create_response(path):
    path = path.replace('/', '\\')
    
    if path == '\\':
        path = '\\index.html'
    
    if not path.endswith(('.html', '.jpg', '.js', '.css', '.ico')):
        path = path + '.html'
    
    if path in FORBIDDEN:
        return "HTTP/1.1 403 Forbidden\r\n".encode()
    
    if path in REDIRECT:
        return "HTTP/1.1 302 Found\r\nLocation: {}\r\n".format(REDIRECT[path]).encode()
    
    try:
        file_content, file_type, length = file_data(path)
        if file_type == 'image/jpeg':
            return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n".format(length, file_type).encode() + file_content
        return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n{}".format(length, file_type, file_content).encode()
    except IsADirectoryError:
        return "HTTP/1.1 404 Not Found".encode()
    except FileNotFoundError as e:
        return "HTTP/1.1 404 Not Found".encode()
    except PermissionError:
        return "HTTP/1.1 404 Not Found".encode()

def handle_client(client_socket):
    while True:
        try:
            request = client_socket.recv(4096).decode()
            end_line = request.index("\r\n")
            request = request[:end_line]
            valid, path = check_request(request)
            if valid:
                response = create_response(path)
                client_socket.send(response)
                break
            else:
                client_socket.send("HTTP/1.1 500 Internal Server Error".encode())
                break 
        except socket.timeout:
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:        
        #create socket bound to port 80 and listen to connection
        server_socket.bind(('0.0.0.0', 80))
        server_socket.listen()
        print("Server is up and running")

        while True:
            (client_socket, client_address) = server_socket.accept() 
            client_socket.settimeout(SOCKET_TIMEOUT)
            handle_client(client_socket)   
            client_socket.close()

if __name__ == "__main__":
    main()