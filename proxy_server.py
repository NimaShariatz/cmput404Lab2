import socket
from threading import Thread

BYTES_TO_READ = 4096
PROXY_SERVER_HOST = "127.0.0.1"
PROXY_SERVER_PORT = 8080

#send some data(request) to host:port
def send_reqeust(host, port, request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        #Connect the socket to host:port
        client_socket.connect((host,port))
        #send the request through the connected socket.
        client_socket.send(request)
        #shut the socket to further writes. Tells server we're doen sending
        client_socket.shutdown(socket.SHUT_WR)
        
        #assemble response, be careful here, recall that recv(bytes) blocks until it recieves data!
        data = client_socket.recv(BYTES_TO_READ)
        result = b'' + data
        while len(data) > 0:
            data = client_socket.recv(BYTES_TO_READ)
            result +=data
        # Return response
        return result
    
def handle_connection(conn, addr):# the important bit is here -------- a proxy acts as a middleman, between the client and server.
    #hence, the proxy needs to act as a client when talking to the google server, and act as a server when talking to the client.
    with conn:
        print(f"Connected by {addr}")
        
        request = b''
        while True: #while the client is keeping the socket open
            data = conn.recv(BYTES_TO_READ) #read some data from the socket
            if not data:#if the socket has been closed to further writes, break.
                break
            print(data)
            request += data
        response = send_reqeust("www.google.com", 80, request) #and send it as a request to www.google.com
        conn.sendall(response) #return the response from ww.google.com back to the client
        # the important bit is here --------
        
def start_server():
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((PROXY_SERVER_HOST,PROXY_SERVER_PORT))
        
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.listen(2)
        
        conn, addr = server_socket.accept()
        
        handle_connection(conn,addr)
        
        
        
def start_threaded_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((PROXY_SERVER_HOST, PROXY_SERVER_PORT))
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.listen(2)
        
        while True:
             conn, addr = server_socket.accept()
             thread = Thread(target=handle_connection, args=(conn, addr))
             thread.run()
    
start_server()
#start_threaded_server()