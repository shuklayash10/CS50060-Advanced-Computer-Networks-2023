import sys
import socket
import threading

# Function to handle incoming client connections
def handle_client(client_socket):
    data = client_socket.recv(1024).decode()
    
    if data:
        print(f"Received: {data} from {client_socket.getpeername()}")
        
        # Echo the received data back to the client
        client_socket.send(data.encode())
    
    # Close the client socket
    client_socket.close()

# Check command line arguments
if len(sys.argv) != 2:
    print("Usage: python TCPPingerConcurrentServer.py <server port no>")
    sys.exit()

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the specified port
server_socket.bind(('', int(sys.argv[1])))
# Listen for incoming connections
server_socket.listen(5)

print(f"Concurrent TCP Pinger Server is listening on port {sys.argv[1]}...")

while True:
    # Accept incoming connection
    client_socket, client_address = server_socket.accept()
    
    # Create a new thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
