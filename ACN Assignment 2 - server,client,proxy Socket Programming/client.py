import sys
import socket
from bs4 import BeautifulSoup
import time

n = len(sys.argv)

serv_address =()
proxy_address =()

proxy_ip  = ''
serv_ip   = ''
proxy_port = ''
serv_port  = ''

if(n>1):
   
   if(n==3):
      #storing the server address
      serv_ip = sys.argv[1]
      serv_port = int(sys.argv[2])
      serv_address = (serv_ip,serv_port)
      
   elif(n==5):
      #storing the server and proxy address
      proxy_ip  = sys.argv[1]
      serv_ip   = sys.argv[2]
      proxy_port = int(sys.argv[3])
      serv_port  = int(sys.argv[4])
      
      proxy_address =(proxy_ip,proxy_port)
      serv_address = (serv_ip,serv_port)

   if(n==3):
      target_address = serv_address
   else:
      target_address = proxy_address
   
   def connect_and_fetch(file_name,target_address):
       
       #creating a new client socket 
       new_client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
       
       #connecting the socket with the main server or proxy server
       new_client_socket.connect(target_address)
       
       request =''
       if n==5:
          request = f"GET http://{serv_address[0]}:{serv_address[1]}/{file_name} HTTP/1.1\nHost: http://{target_address[0]}:{target_address[1]}"
       
       else:
         #creating a get message 
         request = f"GET {file_name} HTTP/1.1\nHost: http://{target_address[0]}:{target_address[1]}"
       
       print("-----------------------------------------------")
       print(f"\nSent a GET request for {file_name} file")
       
       
       new_client_socket.send(request.encode())

       response = new_client_socket.recv(8192)
       
       header_end = response.find(b'\r\n\r\n')
       header = response[:header_end]
   
       print("\nReply from the server:")
       print(header.decode())
       
       if response.find(b'404')!=-1:
         print(response.decode())
         new_client_socket.close()
         return
       
       
       header_end = response.find(b'\r\n\r\n')
       
       file_path = 'assets/'+file_name
       
       response = response[header_end+4:]
       
       #end_ind = request.find("HTTP")
       #file_path = request[start_ind:end_ind].strip()
   
       with open(file_path,"wb") as img_file:
          img_file.write(response)
          
       #print(response)
       
       new_client_socket.close()   
   
   html_req=''
   
   if(n==5):
      
      #creating a get message for html file 
      html_req = f"GET http://{serv_address[0]}:{serv_address[1]}/ HTTP/1.0\nHost: http://{target_address[0]}:{target_address[1]}"
      
   else:
     #creating a get message for html file 
     html_req = f"GET index.html HTTP/1.1\nHost: http://{target_address[0]}:{target_address[1]}"
   
   print("-----------------------------------------------")
   print("\nSent a GET request for HTML file")
   # Creating a socket object
   client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
      
   #connecting the socket with the main server or proxy server
   client_socket.connect(target_address)

   client_socket.send(html_req.encode())

   response = client_socket.recv(4096).decode()
   
   ind = response.find('<!DOCTYPE html>')
   header = response[:ind]
   
   print("\nReply from the server:")
   print(header)
   
   client_socket.close()

   html_content = response[ind:].strip()
   
   file_path = "assets/index1.html"
   
   with open(file_path,"w") as html_file:
      html_file.write(html_content)

   soup = BeautifulSoup(html_content, 'html.parser')
   
   referenced_objects = []

   #Extract images
   img_elements = soup.find_all('img')
   for img in img_elements:
      image_url = img.get('src')
      if image_url:
          referenced_objects.append(image_url)
   
   
   
   for obj in referenced_objects:
      connect_and_fetch(obj,target_address)
   
else:
   print("Invalid address provided please check again....!!")
         
