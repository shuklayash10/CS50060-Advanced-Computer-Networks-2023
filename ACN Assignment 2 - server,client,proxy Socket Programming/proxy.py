import socket
import threading

# Proxy Address
proxy_address = ('172.18.3.8', 12348)

# Creating a socket object
proxy_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 

proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# Binding the socket to the proxy address and port
proxy_socket.bind(proxy_address)

#make the proxy to listen for incoming connections by client
proxy_socket.listen(5)


def proxy_serv(client_socket,serv_address):
    
    # Creating a socket object
    proxy_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    #connecting the socket with the main server 
    proxy_client.connect(serv_address)
    
    # Receive the client's request
    request = client_socket.recv(8192).decode('utf-8')
    print("-----------------------------------------------")
    print("\nRequest by the client:")
    print(request)
    
    # Check if it's an HTTP GET request
    if "GET " in request:
        
        header = f"GET http://{serv_address[0]}:{serv_address[1]}/"
        
        ind = request.find("HTTP")
        
        file_name = request[len(header):ind].strip()
        
        request = f"GET {file_name} HTTP/1.1\nHost: http://{serv_address[0]}:{serv_address[1]}"
        
        proxy_client.send(request.encode('utf-8'))
        
        response = proxy_client.recv(8192)
        
        ind = response.find(b'\r\n\r\n')
        header = response[:ind]
        
        print("\nReply from the server:")
        print(header.decode())
        
        client_socket.send(response)

    # Close the client socket
    client_socket.close()
    
#-------------------------------------------------------------------------------

try:

    # Accept a connection from a client
    client_socket, client_address = proxy_socket.accept()
    
    #creating a seperate thread for every connection request
    print(f"Accepted connection from {client_address}")
    
    request=client_socket.recv(8192).decode()
    print("-----------------------------------------------")
    print("\nRequest by client:")
    print(request)
    
    start_ind = 11
    end_ind = request.find('/ HTTP')
    serv_add = request[start_ind:end_ind].strip()
    
    ind = serv_add.find(':')
    
    serv_ip = serv_add[:ind].strip()
    serv_port = int(serv_add[ind+1:].strip())
    
    #creating server address and port from msgs sent by client
    serv_address=(serv_ip,serv_port)
    
    # Creating a socket object
    proxy_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    try:
      #connecting the socket with the main server 
      proxy_client.connect(serv_address)
    
      print(f"\nConnected with the server at {serv_address}\n")

      # Check if it's an HTTP GET request
      if "GET " in request:
	
        request = f"GET index.html HTTP/1.1\nHost: http://{serv_address[0]}:{serv_address[1]}"
        
        proxy_client.send(request.encode('utf-8'))
        
        response = proxy_client.recv(8192)
        
        ind = response.find(b'<!DOCTYPE html>')
        header = response[:ind]
   
        print("\nReply from the server:")
        print(header)
        
        client_socket.send(response)
    
      client_socket.close()
      proxy_client.close()
    
      thread_arr=[]
    
      while True:
      
        # Accept a connection from a client
        client_socket, client_address = proxy_socket.accept()
      
        #creating a seperate thread for every connection request
        print(f"Accepted connection from {client_address}")	
      
        proxy_thread = threading.Thread(target = proxy_serv,args=(client_socket,serv_address))
      
        proxy_thread.start()
      
        thread_arr.append(proxy_thread)
      
      for t in thread_arr:
        t.join()
    
      proxy_socket.close()         
    except :
      
      print("\n.....Communication error with the requested server.....!!!\n")
          
except Exception as e:
  print(e)
  proxy_socket.close()
  print("Keyboard Interrupt")
