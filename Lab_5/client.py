import socket   #for sockets
import sys      #for exit
from check import ip_checksum

# Create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # if socket functions fail, catch exception
except socket.error, msg:
    print('Failed to create socket')
    sys.exit()


host = 'localhost'
port = 8888

# Packet # counter
n = 0
while(1):
    # msg = raw_input('Enter message to send: ')
    msg = 'packet' + n

    try:
        # Set the whole string
        s.sendto(msg, (host, port))

        # Receive data from client (data, addr)
        d = s.recvfrom(1024)
        reply = d[0]
        addr = d[1]

        # Send first 3 packets normally
        if reply == 'ack packet' + n:
            print('ack packet' + n + 'received')
            n += 1

        # Send 3 packets where 2nd packet is corrupted
        # If data corrupted, resend
        elif ip_checksum(d) != 0:
            s.sendto(msg, (host, port))

        # Send 3 packets where 2nd packet times out (delay ack)
        # If packet times out, resend
        elif timeout:
            s.sendto(msg, (host, port))

            

        # print('Server reply: ' + reply)
    
    except socket.error, msg:
        print('Error Code: ' + str(msg[0]) + 'Message' + msg[1])
        sys.exit()
    n += 1
