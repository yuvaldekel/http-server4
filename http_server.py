import socket
import re
import os 

WWW_PATH = r"C:\Users\yonat\Documents\Yuval\devops\networking\http-server4\wwwroot"
UPLOADS  = "C:\\Users\\yonat\\Documents\\Yuval\\devops\\networking\\http-server4\\wwwroot\\uploads\\"
SOCKET_TIMEOUT = 1
REDIRECT  = {'\\index1.html': '\\index.html'}
FORBIDDEN = {'\\index3.html'}

def check_request(request):
    content_length = None
    path = None
    valid = False

    end_line = request.index("\r\n")
    request_line = request[:end_line]
    
    if  re.search("^((GET )|(POST ))((\/[a-zA-Z0-9=\-_\.\?&]{0,}){1,})( HTTP\/[1-9\.]+)$", request_line):
        valid = True
        path = request_line.split(' ')[1]
        method = request_line.split(' ')[0]
        if method == "POST":
            content_length = get_content_length(request)
    return valid, method, path, content_length

def get_content_length(request):
    if "Content-Length: " in request:
        return int(request[request.index("Content-Length: ")+16:request.index("\r\n",request.index("Content-Length:"))])
    
def get_file_data(path):
    file_type = path.split('.')[-1]
    if file_type == 'txt' or file_type == 'html':
        file_type = "text/html; charset=utf-8"
        with open(WWW_PATH + path, 'r', encoding="utf8") as file:
            file_content = file.read()
        return file_content, file_type, len(file_content)
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
    if file_type == 'gif':
        file_type = "image/gif"
        with open(WWW_PATH + path, 'rb') as file:
            file_content = file.read()
        return file_content, file_type, os.path.getsize(WWW_PATH + path)

    else:
        raise ValueError 

def post_image(path, data):

    if not path.endswith(".jpg") and "file_name" not in path:
        raise ValueError
    file_name = path[path.index('file-name=')+10:]
    if os.path.isfile(UPLOADS + file_name):
        raise ValueError
    with open(UPLOADS + file_name, 'wb') as file:
            file.write(data)
            return file_name, len(data)
    
def send_image(path):
    if not path.endswith('.jpg'):
        path = path + '.jpg'
    if "image-name=" not in path:
        raise ValueError
    image_name = "\\uploads\\" + path[path.index('image-name=')+11:]
    return get_file_data(image_name)

def get_next(path):  
    if 'num=' not in path:
        raise ValueError
    number = int(path[path.index('num=') + 4:])
    next = number + 1 
    return next, len(str(next))

def area(path):
    if 'height=' not in path and "width=" not in path:
        raise ValueError
    height = int(path[path.index('height=') + 7: path.index('&')])
    width = int(path[path.index('width=')+6:])
    if  width * height % 2 == 0:
        value = width * height // 2
    else:
        value = width * height / 2
    return value, len(str(value))

def GET(path):
    if path.startswith('\\calculate-next?'):
        try:
            next, length = get_next(path)
            return f"HTTP/1.1 200 OK\r\nContent-Length: {length}\r\nContent-Type: text/plain\r\n\r\n{next}".encode()
        except ValueError:
            return "HTTP/1.1 400 Bad Request\r\n".encode()
        except:
            return "HTTP/1.1 500 Internal Server Error".encode()

    if path.startswith('\\calculate-area?'):
        try:
            area_value, length = area(path)
            return f"HTTP/1.1 200 OK\r\nContent-Length: {length}\r\nContent-Type: text/plain\r\n\r\n{area_value}".encode()
        except ValueError:
            return "HTTP/1.1 400 Bad Request\r\n".encode()    
        except:
            return "HTTP/1.1 500 Internal Server Error".encode()
    
    if path.startswith('\\image?'):
        try:
            image_content, content_type, length = send_image(path)
            return f"HTTP/1.1 200 OK\r\nContent-Length: {length}\r\nContent-Type: {content_type}\r\n\r\n".encode() + image_content
        except IsADirectoryError:
            return "HTTP/1.1 404 Not Found".encode()
        except FileNotFoundError:
            return "HTTP/1.1 404 Not Found".encode()
        except PermissionError:
            return "HTTP/1.1 404 Not Found".encode()
        except ValueError:
            return "HTTP/1.1 404 Not Found".encode()
        except:
            return "HTTP/1.1 500 Internal Server Error".encode()

    if not path.endswith(('.html', '.jpg', '.js', '.css', '.ico', 'gif')):
        path = path + '.html'
    
    if path in FORBIDDEN:
        return "HTTP/1.1 403 Forbidden\r\n".encode()
    
    if path in REDIRECT:
        return "HTTP/1.1 302 Found\r\nLocation: {}\r\n".format(REDIRECT[path]).encode()
    
    try:
        file_content, file_type, length = get_file_data(path)
        if file_type == 'image/jpeg' or file_type == 'image/gif':
            return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n".format(length, file_type).encode() + file_content
        return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n{}".format(length, file_type, file_content).encode()
    except IsADirectoryError:
        return "HTTP/1.1 404 Not Found".encode()
    except FileNotFoundError as e:
        return "HTTP/1.1 404 Not Found".encode()
    except PermissionError:
        return "HTTP/1.1 404 Not Found".encode()
    except ValueError:
        return "HTTP/1.1 404 Not Found".encode()
    except:
        return "HTTP/1.1 500 Internal Server Error".encode()


def POST(path, body):
    if path in FORBIDDEN:
        return "HTTP/1.1 403 Forbidden\r\n".encode()
    
    if path in REDIRECT:
        return "HTTP/1.1 302 Found\r\nLocation: {}\r\n".format(REDIRECT[path]).encode()
    
    if path.startswith('\\upload'):
        try:
            file_name, image_length = post_image(path, body) 
            return "HTTP/1.1 200 OK\r\n\r\nfile {} of size {} was saved successfully".format(file_name, image_length).encode()
        except ValueError:
            return "HTTP/1.1 400 Bad Request\r\n".encode()
        except IOError:
            return "HTTP/1.1 500 Internal Server Error".encode()
        except:
            return "HTTP/1.1 500 Internal Server Error".encode()
 

def create_response(method, path, body):
    path = path.replace('/', '\\')
    if path == '\\':
        path = '\\index.html'

    if method == "GET":
        return GET(path)
    if method == "POST":
        return POST(path, body)

def handle_client(client_socket): 
    body = None
    while True:
        try:
            request = client_socket.recv(2048).decode()

            valid, method, path, content_length = check_request(request)
            if valid:

                if content_length != None:
                    body = client_socket.recv(content_length)
                    while len(body) != content_length:
                        body = body + client_socket.recv(content_length)
                
                response = create_response(method, path, body)
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
            print(f"client connected {client_address[0]}")
            client_socket.settimeout(SOCKET_TIMEOUT)
            handle_client(client_socket)   
            client_socket.close()

if __name__ == "__main__":
    main()