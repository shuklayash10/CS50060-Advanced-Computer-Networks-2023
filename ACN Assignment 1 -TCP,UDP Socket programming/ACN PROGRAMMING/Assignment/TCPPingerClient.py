import sys
import socket

# Check command line arguments
if len(sys.argv) != 3:
    print("Usage: python TCPPingerClient.py <server hostname> <server port no>")
    sys.exit()

server_host = sys.argv[1]
server_port = int(sys.argv[2])

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((server_host, server_port))

# Send a ping message to the server
message = "Ping"
client_socket.send(message.encode())

# Receive the response from the server
response = client_socket.recv(1024).decode()

print(f"Received: {response}")

# Close the socket
client_socket.close()
