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
window_start = 0
window = []

# Set up initial packet
# Scenario 1: Packets 0-2
while n < 3:
    msg = 'packet ' + str(n)
    check_sum = ip_checksum(msg)
    msg += ';' + str(ord(check_sum[0]) + ord(check_sum[1]))
    s.sendto(msg, (host, port))
    window.append(n)
    n += 1

while(window_start < 12):
    # msg = raw_input('Enter message to send: ')
    # print('check_sum ' + str(ord(check_sum[0])) + '; pt 2: ' + str(ord(check_sum[1])))

    try:
        if not window:
            break
        """
        if n == 6:
            timer.start()
        """
        print('client: window = ' + str(window))

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

        parsed_reply = reply.split('packet', 1)
        acked = int(parsed_reply[1])
        #print('acked = ' + str(acked))
        if 'ack packet' in reply:
            print('ack packet ' + str(acked) + ' received\n')

            # If first value of window is acked, slide window down
            if acked == window_start:
                window.remove(acked)
                window_start = acked + 1
            
                # Send next packet
                if n < 12:
                    print('New window start = ' + str(window_start) + '\n')
                    msg = 'packet ' + str(n)
                    check_sum = ip_checksum(msg)
                    msg += ';' + str(ord(check_sum[0]) + ord(check_sum[1]))
                    s.sendto(msg, (host, port))
                    window.append(n)
                    n += 1
            else:
                window.remove(acked)
    
    except socket.error, msg:
        print('Error Code: ' + str(msg[0]) + 'Message' + msg[1])
        sys.exit()
