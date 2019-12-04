import socket
import sys
from thread import *

userpw = {'user1': 'pw1', 'user2': 'pw2', 'user3': 'pw3'}
# Key is user, value is users subscribed to
subs = {'user1': [], 'user2': [], 'user3': []}
tweets = {'user1': {}, 'user2': {}, 'user3': {}}

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
    current_user = ""
    #sending message to connected client
    conn.send('\nWelcome to the CS164 Twitter Knockoff!\nPlease enter your username: ') #send only takes string
    current_user = conn.recv(1024)
    while current_user not in userpw:
        conn.send('\nPlease enter a valid username: ')
        current_user = conn.recv(1024)

    conn.send('\nPlease enter your password: ')
    password_in = conn.recv(1024)
    while password_in != userpw[current_user]:
        conn.send('\nPassword not accepted. Please try again: ')
        password_in = conn.recv(1024)

    conn.send('\nLogin successful. Welcome back!\n')

    unread = 0
    msg = '\nYou have ' + str(unread) + ' unread messages'
    conn.sendall(msg)

    #infinite loop so that function do not terminate and thread do not end.
    while True:
        msg = '\n\nPlease select an option: \n'
        msg += '1) See offline messages\n'
        msg += '2) Edit subscriptions\n'
        msg += '3) Post a message\n'
        msg += '4) Logout\n'
        msg += '5) Hashtag search\n'
        conn.sendall(msg)

        data = conn.recv(1024)
        while data != '1' and data != '2' and data != '3' and data != '4' and data != '5':
            conn.sendall('\nPlease enter a valid selection')
            data = conn.recv(1024)

        # See offline messages
        if data == '1':
            msg = "Offline Messages Menu\nPlease select an option:\n"
            msg += '1) See all messages'
            msg += '2) See messages from specific user'
            msg += '3) Return to main menu\n'
            conn.sendall(msg)
            sel = conn.recv(1024)
            while sel != '1' and sel != '2' and sel != '3':
                conn.sendall('\nPlease enter a valid selection')
                sel = conn.recv(1024)
            # Display all messages made by subscribed users while current user was offline
            if sel == '1':
                # TODO: THE ACTUAL TWEETS THING
                msg = 'do dis.'

            # View specific user's offline tweets
            elif sel == '2':
                quit = False
                msg = 'Please enter the username you would like to view offline tweets of:'
                conn.sendall(msg)
                sub_user = conn.recv(1024)
                while sub_user not in subs[current_user] and not quit:
                    conn.send('\nPlease enter a valid username or \'0\' to exit: ')
                    sub_user = conn.recv(1024)
                    if sub_user == '0':
                        quit = True
                if quit:
                    conn.send('\nReturning to main menu')
                    continue
                # TODO: THE ACTUAL TWEETS THING

            # Return to main menu
            elif sel == '3':
                conn.send('\nReturning to main menu')
                continue

        # Edit subscriptions
        elif data == '2': 
            msg = "\n\nEdit Subscriptions Menu\nPlease select an option:\n"
            msg += '1) Add a subscription\n'
            msg += '2) Drop a subscription\n'
            msg += '3) Return to main menu\n'
            conn.sendall(msg)
            sel = conn.recv(1024)
            while sel != '1' and sel != '2' and sel != '3':
                conn.sendall('\nPlease enter a valid selection')
                sel = conn.recv(1024)

            # Add a subscription
            if sel == '1':
                quit = False
                msg = 'Please enter the username you would like to subscribe to:'
                conn.sendall(msg)
                sub_user = conn.recv(1024)
                while sub_user not in userpw and not quit:
                    conn.send('\nPlease enter a valid username or \'0\' to exit: ')
                    sub_user = conn.recv(1024)
                    if sub_user == '0':
                        quit = True
                if quit:
                    conn.send('\nReturning to main menu')
                    continue

                if sub_user in subs[current_user]:
                    msg = '\nYou are already subscribed to ' + sub_user
                    conn.send(msg)
                else: 
                    subs[current_user].append(sub_user)
                    msg = '\nSuccessfully subscribed to ' + sub_user

                # Print current subscriptions
                msg += '\nYour current subscriptions: '
                conn.send(msg)
                for subbed in subs[current_user]:
                    msg = '\n\t' + subbed
                    conn.send(msg)

            # Remove a subscription
            elif sel == '2':
                quit = False

                # Print current subscriptions
                msg += '\nYour current subscriptions: '
                conn.send(msg)
                for subbed in subs[current_user]:
                    msg = '\n\t' + subbed
                    conn.send(msg)

                msg = 'Please enter the username you would like to unsubscribe from:'
                conn.sendall(msg)
                sub_user = conn.recv(1024)
                while sub_user not in subs[current_user] and not quit:
                    conn.send('\nPlease enter a valid username you are currently subscribed to or \'0\' to exit: ')
                    sub_user = conn.recv(1024)
                    if sub_user == '0':
                        quit = True
                if quit:
                    conn.send('\nReturning to main menu')
                    continue

                subs[current_user].remove(sub_user)
                msg = '\nSuccessfully unsubscribed from: ' + sub_user

            # Return to main menu
            elif sel == '3':
                conn.send('\nReturning to main menu')
                continue

        # Post a message
        elif data == '3':
            quit = False
            # Post a message
            # reply = data[len('!sendall'):]
            msg_out = '\nPlease enter a message of 140 chars or less'
            conn.sendall(msg_out)
            tweet = conn.recv(1024)
            while len(tweet) > 140:
                msg_out = '\nMessage must be 140 chars or less. Please try again or enter \'0\' to return to main menu: \n'
                conn.sendall(msg_out)
                tweet = conn.recv(1024)
                if tweet == '0':
                    quit = True
            if quit:
                conn.send('\nReturning to main menu')
                continue
            tweets[current_user][tweet] = []
            while not quit:
                msg_out = '\nPlease enter hashtags prepended by \'#\' and separated by newlines, or press \'0\' to proceed:'
                conn.sendall(msg_out)
                hashtag = conn.recv(1024)
                if hashtag == '0':
                    msg_out = '\nProceeding..'
                    conn.sendall(msg_out)
                    quit = True
                elif hashtag[0] != '#':
                    msg_out = '\nPlease prepend the hashtag with \'#\' or enter \'0\' to proceed:'
                    conn.sendall(msg_out)
                    hashtag = conn.recv(1024)
                    tweets[current_user][tweet].append(hashtag)
                else:
                    tweets[current_user][tweet].append(hashtag)

            """
            msg_out = '\nMessage from ' + current_user + ': ' + msg_in
            for c in clients:
                if c != conn:
                    c.sendall(msg_out)
            """
            msg_out = '\nTweet posted'
            conn.sendall(msg_out)

            # TEST REMOVE
            msg = '\nYour tweets: '
            conn.sendall(msg)
            for tweet in tweets[current_user]:
                msg = '\n* ' + tweet
                for hashtags in tweets[current_user][tweet]:
                    msg += ' ' + hashtags
                conn.sendall(msg)

        elif data == '4':
            msg = current_user + ' logging out...'
            conn.sendall(msg)
            break

        # Hashtag search
        elif data == '5':
            quit = False
            msg = '\nPlease enter a hashtag to search prepended by \'#\' or enter \'0\' to return to main menu'
            conn.sendall(msg)
            hashtag_in = conn.recv(1024)
            while hashtag_in[0] != '#' and hashtag_in != '0':
                msg = '\nPlease prepend hashtag with \'#\' or enter \'0\' to return to main menu'
                conn.sendall(msg)
                hashtag_in = conn.recv(1024)
                if hashtag_in == '0':
                    quit = True
            if quit:
                conn.send('\nReturning to main menu')
                continue
            n = 1
            for user in tweets:
                if n > 10:
                    break
                for tweet in tweets[user]:
                    if n > 10:
                        break

                    for hashtags in tweets[user][tweet]:
                        if hashtag_in == hashtags:
                            msg = '\n' + str(n) + ') Tweet from @' + user + ': \"' + tweet
                            for hashtags in tweets[user][tweet]:
                                msg += ' ' + hashtags
                            msg += '\"'
                            conn.sendall(msg)
                            n += 1
            if n == 1:
                conn.sendall('\nNo tweets containing ' + hashtag_in + ' found.')

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
