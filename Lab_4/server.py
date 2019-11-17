import socket
import sys
from thread import *

HOST = ''   # Symbolic name meaning all available interfaces
# NOTE: Cannot have 2 sockets bound to the same port
PORT = 8888 # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error, msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

s.listen(10) # 10 connections can wait to be processed before 11th is rejected
print 'Socket now listening'

# Create a set of clients to cycle through for !sendall command
# Referred to: https://stackoverflow.com/questions/27139240/i-need-the-server-to-send-messages-to-all-clients-python-sockets
clients = set()

# Function for handling connections. This will be used to create threads
def clientthread(conn):
    #sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string

    #infinite loop so that function do not terminate and thread do not end.
    while True:
       #Receiving from client
       msg = '# loop begin\n'
       # conn.sendall(msg)

       data = conn.recv(1024)
       if not data or data.startswith('!q'):
           msg = '# exiting...'
           conn.sendall(msg)
           break
       if data.startswith('!sendall'):
           reply = data[len('!sendall'):]
           for c in clients:
               c.sendall(reply)
       else:
           reply = 'OK...' + data
           conn.sendall(reply)
       
    #came out of loop
    conn.sendall('# removing & closing')
    clients.remove(conn)
    conn.close()

# Now keep talking with the client
# Now socket_accept is in a loop
while 1:
    # Wait to accept a connection - blocking call
    # Not sure what this syntax refers to
    conn, addr = s.accept()

    # Display client information
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    clients.add(conn)
    start_new_thread(clientthread ,(conn,))

# conn.close()
# for conn in clients:
#    clients.remove(conn)
s.close()
