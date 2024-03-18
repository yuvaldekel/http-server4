import socket

def main():
    with socket.socket() as server_socket:
        #create socket bound to port 80 and listen to connection
        server_socket.bind(('0.0.0.0', 80))
        server_socket.listen()
        print("Server is up and running")

        while True:
            (client_socket, client_address) = server_socket.accept()

if __name__ == "__main__":
    main()