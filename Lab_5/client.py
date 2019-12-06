import socket   #for sockets
import sys      #for exit
from check import ip_checksum
import threading #for timeout

timeout = False
msg = ''
n = ''

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # if socket functions fail, catch exception
except socket.error, msg:
    print('Failed to create socket')
    sys.exit()


host = 'localhost'
port = 8888

def pkt_timer():
    timeout = True
    print('\nTimeout detected')
    print('Resending timed-out packet ' + str(n) + '\n')
    s.sendto(msg, (host, port))
timer = threading.Timer(3.0, pkt_timer)

# Create dgram udp socket

# Client is sender

# Packet # counter
n = 0

# Set up initial packet
# Scenario 1: Packets 0-2
print('\nSending 3 packets normally:\n')
msg = 'packet ' + str(n)
check_sum = ip_checksum(msg)
msg += ';' + str(ord(check_sum[0]) + ord(check_sum[1]))
s.sendto(msg, (host, port))

while(n < 9):
    # msg = raw_input('Enter message to send: ')
    # print('check_sum ' + str(ord(check_sum[0])) + '; pt 2: ' + str(ord(check_sum[1])))

    try:
        if n == 6:
            timer.start()

        # Receive data from client (data, addr)
        d = s.recvfrom(1024)
        reply = d[0]
        addr = d[1]

        # If data corrupted, resend
        if 'CORRUPTED: ' in reply:
            print('Resending corrupted packet ' + str(n))
            s.sendto(msg, (host, port))

        # Send 3 packets where 2nd packet times out (delay ack)
        # If packet times out, resend
        elif timeout:
            print('Resending timed-out packet ' + str(n))
            s.sendto(msg, (host, port))

        if reply == 'ack packet ' + str(n):
        #else:
            print('ack packet ' + str(n) + ' received')
            
            # Send next packet
            if n >= 8:
                break
            n += 1
            # Scenario 2: Packets 3-5
            if n == 3:
                print('\nSending 3 packets where second packet (pkt 4) has invalid checksum:\n')
            # Scenario 3: Packets 6-8
            if n == 6:
                print('\nSending 3 packets where second packet (pkt 7) times out:\n')
            msg = 'packet ' + str(n)
            check_sum = ip_checksum(msg)
            msg += ';' + str(ord(check_sum[0]) + ord(check_sum[1]))
            s.sendto(msg, (host, port))

        # print('Server reply: ' + reply)
    
    except socket.error, msg:
        print('Error Code: ' + str(msg[0]) + 'Message' + msg[1])
        sys.exit()
