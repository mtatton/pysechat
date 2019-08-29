# telnet program example
import socket
import select
import string
import ssl
import curses
import traceback
import sys

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
      print_message_my(idx,val[0]);
    else:
      print_message_other(idx,val[0]);

def print_message_my(idx,val):
  #stdscr.addstr(1+idx,0,str(1+idx) + ": " + val,curses.color_pair(2))
  stdscr.addstr(1+idx,0,str(1+idx) + ": " + val)

def print_message_other(idx,val):
  #stdscr.addstr(1+idx,0,str(1+idx) + ": " + val,curses.color_pair(3))
  stdscr.addstr(1+idx,0,str(1+idx) + ": " + val)

def process_message(msg,source):
  if (msg=="quit"):
    s.send("Goodbye")
    s.close()
    curses.endwin()
    sys.exit()
  else:
    messages.append([msg,source])
    if (len(messages)>20):
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
    read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [],0.01)
    
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
