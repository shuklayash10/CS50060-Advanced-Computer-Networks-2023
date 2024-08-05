import sys
import socket
import random
import time

# Check command line arguments
if len(sys.argv) != 3:
    print("Usage: python TCPPingerModifiedServer.py <server port no> <packet loss probability>")
    sys.exit()

server_port = int(sys.argv[1])
packet_loss_prob = float(sys.argv[2])

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the specified port
server_socket.bind(('', server_port))
# Listen for incoming connections
server_socket.listen(1)

print(f"TCP Pinger Modified Server is listening on port {server_port}...")

while True:
    # Accept incoming connection
    client_socket, client_address = server_socket.accept()

    # Generate a random number between 0 and 1 to simulate packet loss
    rand = random.random()

    if rand < packet_loss_prob:
        # Simulate packet loss
        print(f"Packet loss to {client_address}")
        time.sleep(1)  # Sleep to simulate packet loss delay
    else:
        # Receive data from the client
        data = client_socket.recv(1024).decode()

        if data:
            print(f"Received: {data} from {client_address}")

            # Echo the received data back to the client
            client_socket.send(data.encode())

    # Close the client socket
    client_socket.close()
