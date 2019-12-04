# Socket client example in python
# Handles errors

import socket   #for sockets
import sys      #for exit

try:
    #create an AF_INET(IPv4), STREAM socket(TCP) (SOCK_DGRAM is UDP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # if socket functions fail, catch exception
except socket.error, msg:
    print 'Failed to create socket. Error code ' + str(msg[0]) + ' , Error message : ' + msg[1]
    sys.exit()

print 'Socket Created'

host = ''
port = 8888

# Try to connect to server
try:
    # Get IP address of remote host
    remote_ip = socket.gethostbyname( host )
except socket.gaierror:
    # could not resolve
    print 'Hostname could not be resolved. Exiting'
    sys.exit()

# We have the IP addr of the remote host/system
print 'IP address of ' + host + ' is ' + remote_ip

# Connect to remote server
s.connect((remote_ip, port))

print 'Socket Connected to ' + host + ' on ip ' + remote_ip

# Maintain connection with server
# Maintain connection with server
# while 1:
#Send some data to remote server
while 1:
    # Now receive data on the socket
    reply = s.recv(4096)
    print reply

    message = raw_input()

    try:
        # Set the whole string
        s.sendall(message)
    except socket.error:
        # Send failed
        print 'Send failed'
        sys.exit()

    if message == '4':
        break

# Close the socket
s.close()
