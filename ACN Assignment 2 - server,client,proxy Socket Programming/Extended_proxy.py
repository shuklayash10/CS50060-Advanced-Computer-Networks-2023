import socket
import threading
from bs4 import BeautifulSoup
import re
import pandas as pd
import matplotlib.pyplot as plt
import sys

#-----------------------------Creating a socket--------------------------------------

# Proxy Address
proxy_address = ('0.0.0.0', 12348)

# Creating a socket object
proxy_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 

proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# Binding the socket to the proxy address and port
proxy_socket.bind(proxy_address)

#make the proxy to listen for incoming connections by client
proxy_socket.listen(5)

#------------------------------------------------------------------------------------

#---------------------------Updating the statistics-------------------------------

browsing_history = pd.read_csv("browsing_history.csv")

browsing_history =browsing_history[["IP","Daily_freq","Weekly_freq","Monthly_freq"]]

'''
print("Read just now")
print(browsing_history)
'''

from datetime import datetime, timedelta

# Function to get the current timestamp with day, week, and month
def get_timestamp():
    now = datetime.now()
    day = now.day
    week = now.strftime("%W")
    month = now.month
    return day, week, month

day, week, month = get_timestamp()

filename = 'last_updated.txt'

with open(filename, 'r') as file:
  last_updated = file.read()

'''
print("\nLast updated is :")
print(last_updated)

print("\nCurrent time stamp:")
print(day,week,month)
'''

last_day,last_week,last_month = map(int,last_updated.split('-'))

if(day!=last_day):

  browsing_history['Daily_freq']=browsing_history['Daily_freq'].apply(lambda x : 0)

if(int(week)!= last_week):
  browsing_history['Weekly_freq']=browsing_history['Weekly_freq'].apply(lambda x : 0)
  print(week,last_week)
if month != last_month:
  browsing_history['Monthly_freq']=browsing_history['Monthly_freq'].apply(lambda x : 0)

with open(filename, 'w') as file:
 file.write(f"{day}-{week}-{month}")

# Function to update the counts for a given IP address
def update_counts(ip_address):

    #browsing_history.set_index('IP', inplace=True) 
    condition = browsing_history['IP']==ip_address
     
    if ip_address in browsing_history['IP'].unique():
        # If the IP address is already in the DataFrame, increment the counts
        browsing_history.loc[condition, 'Daily_freq'] += 1
        browsing_history.loc[condition, 'Weekly_freq'] += 1
        browsing_history.loc[condition, 'Monthly_freq'] += 1
        
        #print(browsing_history.head())
    else:
        # If the IP address is not in the DataFrame, create a new row with all counts=1
       browsing_history.loc[len(browsing_history)] = [ip_address,1, 1, 1]
   
    print(browsing_history)
    browsing_history.to_csv('browsing_history.csv')
      
#--------------------------------------------------------------------------------------

#----------------------------usage Statistic Analysis----------------------------------

def pie_chart_(key,browsing_history):
  
  # Extract IP addresses and their corresponding day visits
  ips = browsing_history.index
  
  visits=''
  
  #print(browsing_history)
  
  if key =="daily":
  
    visits = browsing_history['Daily_freq'].values
   
  elif key == "weekly":
    visits = browsing_history['Weekly_freq'].values
    
  else:
    visits = browsing_history['Monthly_freq'].values
  
  print(visits)
  # Create a pie chart
  plt.figure(figsize=(6, 6))
  plt.pie(visits, labels=ips, autopct='%1.1f%%', startangle=140)
  plt.title('Frequency of IP Addresses Visited in a '+str(key))
  plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
  plt.savefig(f'{key}.png')
  
  
  

#-------------------------------------------------------------------------------------

#--------------------------Blocklist and Offfensive words Filtering -----------------

#blocklist of hosts
blocklist=['123.5.6.7','122.34.32.2','171.32.200.12']#,'0.0.0.0']

#list of offensive words
offensive_words = ["crime","cheat","hate","kill","fight","blackmail","rob","unfair"]

#Function to filter out the offensive words
def filter_content(response):

    start_ind = response.find("<!DOCTYPE html>")
    html_content = response[start_ind:].strip()

    soup = BeautifulSoup(html_content, 'html.parser')
        
    for word in offensive_words:
          for element in soup.find_all(text=re.compile(re.escape(word))):
            
            element.replace_with(element.replace(word,'***offensive***'))
        
    html_content = str(soup)

    response = response[:start_ind]+html_content
    
    return response

#------------------------------------------------------------------------------------


#--------------------Thread to handle a request--------------------------------------

def proxy_serv(client_socket,serv_address):
    
    # Creating a socket object
    proxy_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    #connecting the socket with the main server 
    proxy_client.connect(serv_address)
    
    # Receive the client's request
    request = client_socket.recv(8192).decode('utf-8')
    print()
    print("----")
    print(request)
    print("----")
    print()
      
    # Check if it's an HTTP GET request
    if "GET " in request:
        
        if "firefox.com" in request:
            sys.exit() 
        
        if serv_ip in blocklist:
    
          response = b"HTTP/1.0 403 Forbidden\n\n<html><h3>403 Forbidden</h3><body>Access to this website is blocked.</body></html>"
          client_socket.send(response)
      
          client_socket.close()
          proxy_client.close()
        
        else:
       
          update_counts(serv_ip)
       
          header = f"GET http://{serv_address[0]}:{serv_address[1]}/"
        
          ind = request.find("HTTP")
        
          file_name = request[len(header):ind].strip()
        
          if file_name =='':
            file_name = "index.html"
        
          request = f"GET {file_name} HTTP/1.0\nHost: http://{serv_address[0]}:{serv_address[1]}"
        
          print(request)
        
          proxy_client.send(request.encode('utf-8'))
        
          response = proxy_client.recv(8192)
        
          if file_name.endswith(".html"):
            print("filtered")
            response = response.decode() 
            response = filter_content(response)
          
          client_socket.send(response)

    # Close the client socket
    client_socket.close()

#---------------------------------------------------------------------------------


#----------------------------initial communication with client--------------------
try:

    # Accept a connection from a client
    client_socket, client_address = proxy_socket.accept()
    
    #creating a seperate thread for every connection request
    print(f"Accepted connection from {client_address}")
    
    request=client_socket.recv(8192).decode()
    
    print("\nRecieved Request from client:\n")
    print(request)
    
    if "analyse" in request:
    
        print(browsing_history)
        #browsing_history.set_index('IP', inplace=True) 
        pie_chart_("daily",browsing_history)
        pie_chart_("weekly",browsing_history)
        pie_chart_("monthly",browsing_history)

        file_name = "usage_stats.html"
        content_type = "text/html"
        start_ind = 11
        end_ind = request.find('/a')
        serv_add = request[start_ind:end_ind].strip()
        ind = serv_add.find(':')
        serv_ip = serv_add[:ind].strip()
        serv_port = int(serv_add[ind+1:].strip())
        
        try:
            
            with open(file_name, 'rb') as file:
                content = file.read()
            response = f"HTTP/1.0 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\n\r\n".encode('utf-8') + content
            client_socket.send(response)
            
            print(response)
            
        except FileNotFoundError:
            response = "HTTP/1.0 404 Not Found\r\n\r\n404 - Not Found".encode()
        print("Reached here 1")
        
        print("Reached here 3")
    
        while True:
      
          # Accept a connection from a client
          client_socket, client_address = proxy_socket.accept()
      
          #creating a seperate thread for every connection request
          print(f"Accepted connection from {client_address}")	
      	  # Receive the client's request
          request = client_socket.recv(8192).decode('utf-8')
          print()
          print("----")
          print(request)
          print("----")
          print()
          
          ind = request.find("HTTP")
          header = f"GET http://{serv_ip}:{serv_port}/"
        
          file_name = request[len(header):ind].strip()
          
          try:
            
            with open(file_name, 'rb') as file:
                content = file.read()
            response = f"HTTP/1.0 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\n\r\n".encode('utf-8') + content
            
          except FileNotFoundError:
            response = "HTTP/1.0 404 Not Found\r\n\r\n404 - Not Found".encode()
          
          client_socket.sendall(response)
          client_socket.close()
          
          '''
          proxy_thread = threading.Thread(target = proxy_serv,args=(client_socket,serv_address))
      
          proxy_thread.start()
      
          thread_arr.append(proxy_thread)'''
      
        for t in thread_arr:
          t.join()
    
        proxy_socket.close()
      	
    else:
    
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
      
      if serv_ip in blocklist:
    
        response = b"HTTP/1.0 403 Forbidden\n\n<html><h3>403 Forbidden</h3><body>Access to this website is blocked.</body></html>"
        client_socket.send(response)
      
        client_socket.close()
        proxy_client.close()
        sys.exit()      
      
      else:
        #connecting the socket with the main server 
        proxy_client.connect(serv_address)
    
        print(f"\nConnected with the server at {serv_address}")

        # Check if it's an HTTP GET request
        if "GET " in request:
          
          if "firefox.com" in request:
            syn.exit()
             
       
          update_counts(serv_ip)
          print("hii")
          request = f"GET index.html HTTP/1.0\nHost: http://{serv_address[0]}:{serv_address[1]}"

          proxy_client.send(request.encode('utf-8'))
        
          response = proxy_client.recv(8192).decode()
        
          start_ind = response.find("<!DOCTYPE html>")
          print("\nReply from the server:\n")
          print(response[:start_ind])
        
          response = filter_content(response)
         
          client_socket.send(response.encode())
        print("Reached here2")
        client_socket.close()
        proxy_client.close()
      
#------------------------------------------------------------------------------------  

#----------------------------multi threading for referenced objects-------------------
      thread_arr=[]
      print("Reached here 3")
    
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
#-------------------------------------------------------------------------------------
        
except Exception as e:
  print(e)
  proxy_socket.close()
  print("Keyboard Interrupt")
      

    
