# PYTHON SSL TCP CHAT CLIENT

import socket
import select
import string
import ssl
import curses
import traceback
import sys

CHAT_ROWS=23
CLR_BLACK=u"\u001b[30m"
CLR_RED=u"\u001b[31m"
CLR_GREEN=u"\u001b[32m"
CLR_YELLOW=u"\u001b[33m"
CLR_BLUE=u"\u001b[34m"
CLR_MAGENTA=u"\u001b[35m"
CLR_CYAN=u"\u001b[36m"
CLR_WHITE=u"\u001b[37m"
CLR_GREEN="\033[31m;"
CTRL_RESET=u"\u001b[0m"
CTRL_RESET="\033[0m;"

stdscr=None
 
messages=[]
s=None

def prompt() :
  stdscr.addstr(0,0,"> ")
  #sys.stdout.write('You> ')
  #sys.stdout.flush()

def print_messages():
  stdscr.clear()
  for idx,val in enumerate(messages):
    if (val[1]==0):
      print_message_my(len(messages)-1-idx,val[0]);
    else:
      print_message_other(len(messages)-1-idx,val[0]);

def print_message_my(idx,val):
  #stdscr.addstr(idx,0,str(1+idx) + ": " + val,curses.color_pair(2))
  stdscr.addstr(idx+1,0,str(1+idx) + ": " + val)

def print_message_other(idx,val):
  #stdscr.addstr(idx,0,str(1+idx) + ": " + val,curses.color_pair(3))
  stdscr.addstr(idx+1,0,str(1+idx) + ": " + val)

def process_message(msg,source):
  if (msg=="quit"):
    s.send("--> Goodbye")
    s.close()
    curses.endwin()
    sys.exit()
  else:
    messages.append([msg,source])
    if (len(messages)>CHAT_ROWS):
      messages.pop(0)  
    print_messages()
    
  #if (msg=="draw"):
    
 
#main function
if __name__ == "__main__":
  
  if(len(sys.argv) < 3) :
    print('Usage : python telnet.py hostname port')
    sys.exit()
  
  host = sys.argv[1]
  port = int(sys.argv[2])
  
  HOSTNAME="127.0.0.1"
  context=ssl.create_default_context() # SSL
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.settimeout(2)
  s = ssl.wrap_socket(sock,certfile='cert.pem',keyfile='key.pem') # SSL
  # connect to remote host
  try :
    s.connect((host, port))
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    print(e)
    print('Unable to connect')
    sys.exit()

  stdscr = curses.initscr()
  curses.echo()
  
  curses.start_color()
  curses.use_default_colors()
  for i in range(0, curses.COLORS):
    curses.init_pair(i + 1, i, -1)

  #stdscr.clear()
  stdscr.refresh()
  
  #print('--- CONNECTED. SEND YOUR MESSAGE')
  stdscr.clear()
  
  while 1:
   
    prompt()
    stdscr.refresh()
    socket_list = [sys.stdin, s]
    
    # Get the list sockets which are readable
    read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
    
    for sock in read_sockets:
      #incoming message from remote server
      if sock == s:
        data = sock.recv(4096)
        if not data :
          print('\nDisconnected from chat server')
          curses.endwin()
          sys.exit()
        else :
          #print data
          #sys.stdout.write(data)
          process_message(data,1)
          prompt()
      
      #user entered a message
      else :
        try:  
          #msg = sys.stdin.readline()
          msg = stdscr.getstr(0,2,77)
          process_message(msg,0)  
          s.send(msg.encode('ascii'))
          prompt()

        except Exception as e:
          print(e)

  curses.endwin()
