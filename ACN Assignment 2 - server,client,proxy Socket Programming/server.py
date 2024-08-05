import socket
import os
import threading

# Server Address
server_address = ('172.18.3.8', 8083)

# Creating a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Binding the socket to the server address and port
server_socket.bind(server_address)

#make the sever to listen for incoming connections
server_socket.listen(5)

def server_func(client_socket):
    
    # Receive the client's request
    request = client_socket.recv(1024).decode('utf-8')
    print("-----------------------------------------------")
    print("\nRecieved Request from client:\n")
    print(request)
    
    # Check if it's an HTTP GET request
    if "GET " in request:
    
        start_ind = 4
        
        if "GET /" in request:
          start_ind =5
        
        end_ind = request.find("HTTP")
        file_name = request[start_ind:end_ind].strip()
        
        if file_name.endswith(".jpeg"): 
            content_type = "image/jpeg"
        
        elif file_name.endswith(".jpg"):
            content_type = "image/jpg"
        
        elif file_name.endswith(".png"):
            content_type = "image/png"
            
        else:
            file_name = "index.html"
            content_type = "text/html"
        
        # Read the content of the file
        try:
            
            with open(file_name, 'rb') as file:
                content = file.read()
            response = f"HTTP/1.0 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\n\r\n".encode('utf-8') + content
            
        except FileNotFoundError:
            response = "HTTP/1.0 404 Not Found\r\n\r\n404 - Not Found".encode()
    
    #print("\nresponse sent\n")
    #print(response)

    # Send the response to the client
    client_socket.sendall(response)

    # Close the client socket
    client_socket.close()
    
try:
    
  print("Server has started...Waiting for incoming connections...")

  thread_arr=[]

  while True:

    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()

    #creating a seperate thread for every connection request
    print(f"Accepted connection from {client_address}")		
    	
    serv_thread = threading.Thread(target = server_func,args=(client_socket,))
    serv_thread.start()
    thread_arr.append(serv_thread)


  for t in thread_arr:
    t.join()

  # Close the server socket
  server_socket.close()

except Exception as e:
  print(e)
  proxy_socket.close()
  print("Keyboard Interrupt")

