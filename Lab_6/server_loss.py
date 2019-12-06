import socket
import sys
from check import ip_checksum
# import threading
import time

HOST = ''
PORT = 8888

reply = ''
addr = ''

"""
def pkt_timer():
    timeout = True
    print('\nSending timed-out ' + reply)
    s.sendto(reply, addr)
timer = threading.Timer(3.1, pkt_timer)
"""

# Datagram (udp) socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created')
except socket.error, msg :
    print('Failed to create socket. Error Code : ' + str(msg[0]) + 'Message ' + msg[1])
    sys.exit()

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print('Bind failed. Error Code: ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

# Server is receiver
corrupted_sent = False
timeout = False
timeout_sent = False

prev = ''
prev_ack = ''

# Now keep talking with the client
while 1:
    d = s.recvfrom(1024)
    data = d[0]
    addr = d[1]

    if not data:
        break
    
    # Split input into data and checksum
    #print('data = ' + str(data))
    data = data.split(';', 1)
    #print('data[1] = ' + data[1])
    checksum_exp = int(data[1])
    data = data[0]

    print('Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip())

    #print('checksum_exp = ' + str(checksum_exp))
    #print('checksum_exp type = ' + str(type(checksum_exp)))
    #print('data = ' + data)

    checksum_actual = ip_checksum(data)
    checksum_actual = ord(checksum_actual[0]) + ord(checksum_actual[1])
    #print('checksum_actual = ' + str(checksum_actual))
    #print('checksum_actual type = ' + str(type(checksum_actual)))

    if not corrupted_sent and data == 'packet 4':
        checksum_actual += 1
        corrupted_sent = True

    if checksum_exp != checksum_actual:
        reply = 'CORRUPTED: ' + data
        print(reply)
        print('\tchecksum_exp = ' + str(checksum_exp))
        print('\tchecksum_actual = ' + str(checksum_actual))

    else:
        reply = 'ack ' + data
        prev_ack = reply

    """
    if not timeout and data == 'packet 7':
        print('Receiver forcing timeout for: ' + data)
        time.sleep(3.1)
        timeout = True
        reply = 'ack ' + data
        prev_ack = reply
        if not timer.isAlive():
            timer.start()
        timeout_sent = True
        reply = 'ack ' + data

    # Duplicate packet received; resend ack
    elif data == prev and timeout:
        reply = prev_ack
        #print('data == prev and timeout')

    else:
    """

    # print('REPLY = ' + reply)
    s.sendto(reply, addr)
    prev = data
