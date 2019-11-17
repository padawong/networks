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

host = 'www.google.com'
port = 80

# Try to connect to server
try:
    # Get IP address of remote host
    remote_ip = socket.gethostbyname( host )
except socket.gaierror:
    # could not resolve
    print 'Hostname could nto be resolved. Exiting'
    sys.exit()

# We have the IP addr of the remote host/system
print 'IP address of ' + host + ' is ' + remote_ip

# Connect to remote server
s.connect((remote_ip, port))

print 'Socket Connected to ' + host + ' on ip ' + remote_ip

#Send some data to remote server
message = "GET / HTTP/1.1\r\n\r\n"

try:
    # Set the whole string
    s.sendall(message)
except socket.error:
    # Send failed
    print 'Send failed'
    sys.exit()

print 'Message send successfully'

# Now receive data on the socket
reply = s.recv(4096)

print reply

# Close the socket
s.close()
