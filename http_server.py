import socket
import re
import os
import datetime
import time 

WWW_PATH = r"C:\Users\yonat\Documents\Yuval\devops\networking\http-server4\wwwroot"
UPLOADS  = "C:\\Users\\yonat\\Documents\\Yuval\\devops\\networking\\http-server4\\wwwroot\\uploads\\"
SOCKET_TIMEOUT = 1
REDIRECT  = {'\\index1.html': '\\index.html'}
FORBIDDEN = {'\\index3.html'}
LOG = r"C:\Users\yonat\Documents\Yuval\devops\networking\http-server4\httpserver.log"
TEMP = r"C:\Users\yonat\Documents\Yuval\devops\networking\http-server4\temp.log"


def write_log(order, **parameter):
    try:
        if order == 1:
            client_log = "{} [{}] ".format(parameter['client_address_arg'],parameter['date_arg'])
        if order == 2:
            client_log = '"{} {}" '.format(parameter['method_arg'], parameter['resource_arg'])
        if order == 3:
            client_log = '{}\n'.format(parameter['status_code_arg'])
        with  open(LOG, 'a') as log_file:
            log_file.write(client_log)
    except Exception as e:
        pass

#check if the request structure is okay
#if it is separate to the http method and http resource 
#if the method is post return also the content length header
def check_request(request):
    content_length = None
    resource = ''
    valid = False
    method = ''

    end_line = request.index("\r\n")
    request_line = request[:end_line]
    
    if  re.search("^((GET )|(POST ))((\/[a-zA-Z0-9=\-_\.\?&%]{0,}){1,})( HTTP\/[1-9\.]+)$", request_line):
        valid = True
        resource = request_line.split(' ')[1]
        method = request_line.split(' ')[0]
        if method == "POST":
            content_length = get_content_length(request)
    return valid, method, resource, content_length

#get http request find the content-length header and return it's value
def get_content_length(request):
    if "Content-Length: " in request:
        return int(request[request.index("Content-Length: ")+16:request.index("\r\n",request.index("Content-Length:"))])
    
#get relative path to a file, take the file type and read it
#return the file length file content and file type by http standard
#if the file type is not one that we suppose to read return raise exception
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

#get resource take from it the image name and save the image
def post_image(resource, data):

    if not resource.endswith(".jpg") and "file_name" not in resource:
        raise ValueError
    file_name = resource[resource.index('file-name=')+10:]
    if os.path.isfile(UPLOADS + file_name):
        raise ValueError
    with open(UPLOADS + file_name, 'wb') as file:
            file.write(data)
            return file_name, len(data)

#get resource take from it which image to read read it using get_file_data
def send_image(resource):
    if "image-name=" not in resource:
        raise ValueError
    image_name = "\\uploads\\" + resource[resource.index('image-name=')+11:]
    if not image_name.endswith('.jpg'):
        image_name = image_name + '.jpg'
    return get_file_data(image_name)

#get resource take the number parameter and return number + 1
def get_next(resource):  
    if 'num=' not in resource:
        raise ValueError
    number = int(resource[resource.index('num=') + 4:])
    next = number + 1 
    return next, len(str(next))

#get resource take the hight and width parameter and calculate area
def area(resource):
    if 'height=' not in resource and "width=" not in resource:
        raise ValueError
    height = int(resource[resource.index('height=') + 7: resource.index('&')])
    width = int(resource[resource.index('width=')+6:])
    if  width * height % 2 == 0:
        value = width * height // 2
    else:
        value = width * height / 2
    return value, len(str(value))

#if the method is get, check the resource
#pass to the correct function depend on the resource
#from the function result create response if the function raised error
#return http error code depend on the exception
def GET(resource):
    if resource in FORBIDDEN:
        return "HTTP/1.1 403 Forbidden\r\n".encode(), '403'
    
    if resource in REDIRECT:
        return "HTTP/1.1 302 Found\r\nLocation: {}\r\n".format(REDIRECT[resource]).encode(), '302'
    
    if resource.startswith('\\calculate-next?'):
        try:
            next, length = get_next(resource)
            return f"HTTP/1.1 200 OK\r\nContent-Length: {length}\r\nContent-Type: text/plain\r\n\r\n{next}".encode(), '200'
        except ValueError:
            return "HTTP/1.1 400 Bad Request\r\n".encode(), '400'
        except:
            return "HTTP/1.1 500 Internal Server Error".encode(), '500'

    if resource.startswith('\\calculate-area?'):
        try:
            area_value, length = area(resource)
            return f"HTTP/1.1 200 OK\r\nContent-Length: {length}\r\nContent-Type: text/plain\r\n\r\n{area_value}".encode(), '200'
        except ValueError:
            return "HTTP/1.1 400 Bad Request\r\n".encode(), '400'
        except:
            return "HTTP/1.1 500 Internal Server Error".encode(), '500'
    
    if resource.startswith('\\image?'):
        try:
            image_content, content_type, length = send_image(resource)
            return f"HTTP/1.1 200 OK\r\nContent-Length: {length}\r\nContent-Type: {content_type}\r\n\r\n".encode() + image_content, '200'
        except IsADirectoryError:
            return "HTTP/1.1 404 Not Found".encode(), '404'
        except FileNotFoundError:
            return "HTTP/1.1 404 Not Found".encode(), '404'
        except PermissionError:
            return "HTTP/1.1 404 Not Found".encode(), '404'
        except ValueError:
            return "HTTP/1.1 404 Not Found".encode(), '404'
        except:
            return "HTTP/1.1 500 Internal Server Error".encode(), '500'

    if not resource.endswith(('.html', '.jpg', '.js', '.css', '.ico', 'gif')):
        resource = resource + '.html'
    
    try:
        file_content, file_type, length = get_file_data(resource)
        if file_type == 'image/jpeg' or file_type == 'image/gif':
            return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n".format(length, file_type).encode() + file_content, '200'
        return "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nContent-Type: {}\r\n\r\n{}".format(length, file_type, file_content).encode(), '200'
    except IsADirectoryError:
        return "HTTP/1.1 404 Not Found".encode(), '404'
    except FileNotFoundError as e:
        return "HTTP/1.1 404 Not Found".encode(), '404'
    except PermissionError:
        return "HTTP/1.1 404 Not Found".encode(), '404'
    except ValueError:
        return "HTTP/1.1 404 Not Found".encode(), '404'
    except:
        return "HTTP/1.1 500 Internal Server Error".encode(), '500'

#if the method is post check the resource
#pass to the correct function with the body depend on the resource
#from the function result create response if the function raised error
#return http error code depend on the exception
def POST(resource, body):
    if resource in FORBIDDEN:
        return "HTTP/1.1 403 Forbidden\r\n".encode(), '403'
    
    if resource in REDIRECT:
        return "HTTP/1.1 302 Found\r\nLocation: {}\r\n".format(REDIRECT[resource]).encode(), '302'
    
    if resource.startswith('\\upload'):
        try:
            file_name, image_length = post_image(resource, body) 
            return "HTTP/1.1 200 OK\r\n\r\nfile {} of size {} was saved successfully".format(file_name, image_length).encode(), '200'
        except ValueError:
            return "HTTP/1.1 400 Bad Request\r\n".encode(), '400'
        except IOError:
            return "HTTP/1.1 500 Internal Server Error".encode(), '500'
        except:
            return "HTTP/1.1 500 Internal Server Error".encode(), '500'
 
#get method resource and body(might be None)
#pass to the correct function
def create_response(method, resource, body):
    resource = resource.replace('/', '\\')
    if resource == '\\':
        resource = '\\index.html'

    if method == "GET":
        return GET(resource)
    if method == "POST":
        return POST(resource, body)

def handle_client(client_socket, client_address): 
    body = None
    while True:
        try:
            request = ''
            i = 0
            while not request.endswith('\r\n\r\n') and i <= 1500:
                request = request + client_socket.recv(1).decode()
                i = i + 1
            
            valid, method, resource, content_length = check_request(request)
            
            write_log(1,client_address_arg = client_address, date_arg = datetime.datetime.now())
            write_log(2,method_arg = method, resource_arg = resource)
            
            if valid:
                if content_length != None:
                    body = client_socket.recv(content_length)
                    i = 0
                    while len(body) != content_length:
                        body = body + client_socket.recv(content_length)

                response, status_code = create_response(method, resource, body)
                client_socket.send(response)

                write_log(3,status_code_arg = status_code)
                break
            else:
                client_socket.send("HTTP/1.1 400 Bad request".encode())
                write_log(3,status_code_arg = '400')
                break 

        except socket.timeout:
            write_log(3,status_code_arg = '500')
            break
        except (ValueError, IndexError) as e:
            client_socket.send("HTTP/1.1 500 Internal Server Error".encode())
            write_log(3,status_code_arg = '500')
            break
        except:
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
            handle_client(client_socket, client_address[0])   
            client_socket.close()

if __name__ == "__main__":
    main()