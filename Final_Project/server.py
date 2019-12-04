import socket
import sys
from thread import *

userpw = {'user1': 'pw1', 'user2': 'pw2', 'user3': 'pw3'}

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
    username_in = ""
    #sending message to connected client
    conn.send('\nWelcome to the CS164 Twitter Knockoff!\nPlease enter your username: ') #send only takes string
    username_in = conn.recv(1024)
    while username_in not in userpw:
        conn.send('\nPlease enter a valid username: ')
        username_in = conn.recv(1024)

    conn.send('\nPlease enter your password: ')
    password_in = conn.recv(1024)
    while password_in != userpw[username_in]:
        conn.send('\nPassword not accepted. Please try again: ')
        password_in = conn.recv(1024)

    conn.send('\nLogin successful. Welcome back!\n')

    unread = 0
    msg = 'You have ' + str(unread) + ' unread messages\n'
    conn.sendall(msg)

    #infinite loop so that function do not terminate and thread do not end.
    while True:
        msg = 'Please select an option: \n'
        msg += '1) See offline messages\n'
        msg += '2) Edit subscriptions\n'
        msg += '3) Post a message\n'
        msg += '4) Logout\n'
        msg += '5) Hashtag search\n'
        conn.sendall(msg)

        data = conn.recv(1024)

        if data == '1':
            # See offline messages
            msg = "See offline messages"

        elif data == '2': 
            # Edit subscriptions
            msg = "edit sub"

        elif data == '3':
            # Post a message
            # reply = data[len('!sendall'):]
            msg = conn.recv(1024)
            while len(msg) > 140:
                print('Message must be 140 chars or less. Please try again: \n')
                msg = conn.recv(1024)
            msg += 'Message from ' + username_in + ': '
            for c in clients:
                c.sendall(msg)

        elif data == '4':
            msg = username_in + ' logging out...'
            conn.sendall(msg)
            break

        elif data == '5':
            # Hashtag search
            msg = "hashtag search"

        else:
            reply = 'Please enter a valid menu item'
            conn.sendall(reply)
       
    #came out of loop
    conn.sendall('\nSuccessfully logged out.')
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
