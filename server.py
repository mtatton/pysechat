# PYTHON SSL TCP CHAT SERVER

import socket
import select
import ssl
import traceback
import os
import sys
import signal

ssock=None

def signal_handler(sig,frame):
  print("\ro--- PROGRAM TERMINATION IN PROGRESS...")
  ssock.close()
  sys.exit(0)

# Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
  #Do not send the message to master socket and the client who has send us the message
  for socket in CONNECTION_LIST:
    if socket != ssock and socket != sock:
      try :
        socket.send(message)
      except :
        # broken socket connection may be, chat client pressed ctrl+c for example
        socket.close()
        CONNECTION_LIST.remove(socket)

if __name__ == "__main__":

  signal.signal(signal.SIGINT, signal_handler)
  # List to keep track of socket descriptors
  CONNECTION_LIST = []
  RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
  PORT = 5000
  HOSTNAME="127.0.0.1"

  context=ssl.create_default_context() # SSL
  context.check_hostname = False
  #context.set_ciphers('ADH-AES256-SHA')
  #context.load_dh_params('cert.pem')

  ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # this has no effect, why ?
  #server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
  ssock = ssl.wrap_socket(ssock,
    keyfile="key.pem",
    certfile="cert.pem",
    server_side=True
  ) # SSL
  ssock.bind((HOSTNAME, PORT))
  ssock.listen(2)

  # Add server socket to the list of readable connections
  # print("APPEND " + str(ssock) + " TO CONNECTION LIST")
  CONNECTION_LIST.append(ssock)

  print("o--- SERVER INIT @ PORT " + str(PORT))

  while 1:
    # Get the list sockets which are ready to be read through select
    try:
      read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[],0.01)
    except Exception as e:
      print("o--- PROGRAM SELECT PHASE ERROR") 
      ssock.close()
      sock.close()
      sys.exit(0)

    for sock in read_sockets:
      # New connection
      if sock == ssock:
      # Handle the case in which there is a new connection recieved through server_socket
        try:
          sockfd, addr = ssock.accept()
          #CONNECTION_LIST.append(sockfd)
          CONNECTION_LIST.append(sockfd)
          print ("|--- CLIENT (%s, %s) CONNECTED" % addr)
          broadcast_data(sockfd, "|--- [%s:%s] ENTERED THE CHAT \n" % addr)
        except Exception as e:
          traceback.print_exc(file=sys.stdout)
          print(e)
          continue

      # Some incoming message from a client
      else:
        # Data recieved from client, process it
        try:
          #In Windows, sometimes when a TCP program closes abruptly,
          # a "Connection reset by peer" exception will be thrown
          data = sock.recv(RECV_BUFFER)
          if data:
            broadcast_data(sock, str(sock.getpeername()[0]) + "> " + data)
        except:
          broadcast_data(sock, "|--- CLIENT (%s, %s) IS OFFLINE" % addr)
          print ("CLIENT (%s, %s) IS OFFLINE " % addr)
          #CONNECTION_LIST.remove(sock) # This caused crashes
          sock.close()
          continue
  
  ssock.close()
