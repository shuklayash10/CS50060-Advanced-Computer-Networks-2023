import random
import sys
from socket import *


if len(sys.argv) != 2:
     print ("Usage: python UDPPingerServer <server port no>")
     sys.exit()


serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.bind(('192.168.36.53', int(sys.argv[1])))

while True:

     rand = random.randint(0, 10)

     message, address = serverSocket.recvfrom(1024)

     message = message.upper()

     if rand < 4:
 	    continue


serverSocket.sendto(message, address)


