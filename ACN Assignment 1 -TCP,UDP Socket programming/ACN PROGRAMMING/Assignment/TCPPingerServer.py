import sys
import socket

# Check command line arguments
if len(sys.argv) != 2:
    print("Usage: python TCPPingerServer.py <server port no>")
    sys.exit()

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the specified port
server_socket.bind(('localhost', int(sys.argv[1])))
# Listen for incoming connections
server_socket.listen(1)

print(f"TCP Pinger Server is listening on port {sys.argv[1]}...")

while True:
    # Accept incoming connection
    client_socket, client_address = server_socket.accept()
    
    # Receive data from the client
    data = client_socket.recv(1024).decode()
    
    if data:
        print(f"Received: {data} from {client_address}")
        
        # Echo the received data back to the client
        client_socket.send(data.encode())
    
    # Close the client socket
    client_socket.close()
