import sys
from socket import *

# Check command line arguments
if len(sys.argv) != 2:
    print("Usage: python UDPPingerServer.py <server port no>")
    sys.exit()

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Assign IP address and port number to socket
serverSocket.bind(('', int(sys.argv[1])))

while True:
    # Receive the client packet along with the address it is coming from
    message, address = serverSocket.recvfrom(1024)
    # Capitalize the message from the client
    message = message.decode().upper()
    
    # Echo the received message back to the client
    serverSocket.sendto(message.encode(), address)
