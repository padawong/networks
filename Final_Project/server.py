import socket
import sys
from thread import *
from datetime import datetime

userpw = {'user1': 'pw1', 'user2': 'pw2', 'user3': 'pw3'}
# Key is user, value is users subscribed to
subbed_to = {'user1': [], 'user2': [], 'user3': []}
subbed_by = {'user1': [], 'user2': [], 'user3': []}
# Key is user, value is another dictionary whose key is a tuple where the first element is the tweet and the second element is the time stamp and the value is the list of hashtags
tweets = {'user1': {}, 'user2': {}, 'user3': {}}
sockets = {'user1': '', 'user2': '', 'user3': ''}
# Key is offline user, value is another dictionary where key is users, value is list of tweets
offline = {'user1': {}, 'user2': {}, 'user3': {}}

def sortTime(tweet_date):
    return tweet_date[0]

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
    sockets[current_user] = conn

    conn.send('\nLogin successful. Welcome back!\n')

    unread = 0
    for user in offline[current_user]:
        for tweet in offline[current_user][user]:
            unread += 1
    msg = '\nYou have ' + str(unread) + ' unread messages\n'
    conn.sendall(msg)

    #infinite loop so that function do not terminate and thread do not end.
    while True:
        # conn.sendall('\n\nCurrent time: ' + str(datetime.now()))
        msg = '\nPlease select an option: \n'
        msg += '1) See offline messages\n'
        msg += '2) Edit subscriptions\n'
        msg += '3) Post a message\n'
        msg += '4) Logout\n'
        msg += '5) Hashtag search'
        conn.sendall(msg)

        data = conn.recv(1024)
        while data != '1' and data != '2' and data != '3' and data != '4' and data != '5':
            conn.sendall('\nPlease enter a valid selection')
            data = conn.recv(1024)

        # See offline messages
        if data == '1':
            # If no unread messages, don't show the menu
            if unread == 0:
                conn.sendall('\nYou have no pending offline messages\n')
                continue

            msg = "\nOffline Messages Menu\nPlease select an option:\n"
            msg += '1) See all messages'
            msg += '\n2) See messages from specific user'
            msg += '\n3) Return to main menu'
            conn.sendall(msg)
            sel = conn.recv(1024)
            while sel != '1' and sel != '2' and sel != '3':
                conn.sendall('\nPlease enter a valid selection')
                sel = conn.recv(1024)
            # Display all messages made by subscribed users while current user was offline
            if sel == '1':
                for user in offline[current_user]:
                    # msg = '\n@' + user
                    for tweet in offline[current_user][user]:
                        msg = '\n@' + user + ': \"' + tweet + '\"'
                        conn.sendall(msg)

            # View specific user's offline tweets
            elif sel == '2':
                quit = False
                msg = '\nPlease enter the username you would like to view offline tweets of:'
                conn.sendall(msg)
                # Print current subscriptions
                msg = '\nYour current subscriptions: '
                conn.send(msg)
                for subbed in subbed_to[current_user]:
                    msg = '\n\t' + subbed
                    conn.send(msg)

                sub_user = conn.recv(1024)
                while sub_user not in subbed_to[current_user] and not quit:
                    conn.send('\nPlease enter a valid username or \'0\' to exit: ')
                    sub_user = conn.recv(1024)
                    if sub_user == '0':
                        quit = True
                if quit:
                    #conn.send('\nReturning to main menu')
                    continue
                if sub_user not in offline[current_user]:
                    conn.sendall('\nThis user has not posted new messages\n')
                    continue
                for tweet in offline[current_user][sub_user]:
                    msg = '\n@' + sub_user + ': \"' + tweet + '\"'
                    conn.sendall(msg)

            # Return to main menu
            elif sel == '3':
                #conn.send('\nReturning to main menu')
                continue

        # Edit subscriptions
        elif data == '2': 
            msg = "\nEdit Subscriptions Menu\nPlease select an option:\n"
            msg += '1) Add a subscription\n'
            msg += '2) Drop a subscription\n'
            msg += '3) Return to main menu'
            conn.sendall(msg)
            sel = conn.recv(1024)
            while sel != '1' and sel != '2' and sel != '3':
                conn.sendall('\nPlease enter a valid selection')
                sel = conn.recv(1024)

            # Add a subscription
            if sel == '1':
                quit = False
                msg = '\nPlease enter the username you would like to subscribe to:'
                conn.sendall(msg)
                sub_user = conn.recv(1024)
                while sub_user == current_user and sub_user not in userpw and not quit:
                    conn.send('\nPlease enter a valid username or \'0\' to exit: ')
                    sub_user = conn.recv(1024)
                    if sub_user == '0':
                        quit = True
                if quit:
                    #conn.send('\nReturning to main menu')
                    continue

                if sub_user in subbed_to[current_user]:
                    msg = '\nYou are already subscribed to ' + sub_user
                    conn.send(msg)
                else: 
                    subbed_to[current_user].append(sub_user)
                    subbed_by[sub_user].append(current_user)
                    msg = '\nSuccessfully subscribed to ' + sub_user

                # Print current subscriptions
                msg += '\nYour current subscriptions: '
                conn.send(msg)
                for subbed in subbed_to[current_user]:
                    msg = '\n\t' + subbed + '\n'
                    conn.send(msg)

            # Remove a subscription
            elif sel == '2':
                quit = False

                # Print current subscriptions
                msg += '\nYour current subscriptions: '
                conn.send(msg)
                for subbed in subbed_to[current_user]:
                    msg = '\n\t' + subbed
                    conn.send(msg)

                msg = '\nPlease enter the username you would like to unsubscribe from:'
                conn.sendall(msg)
                sub_user = conn.recv(1024)
                while sub_user not in subbed_to[current_user] and not quit:
                    conn.send('\nPlease enter a valid username you are currently subscribed to or \'0\' to exit: ')
                    sub_user = conn.recv(1024)
                    if sub_user == '0':
                        quit = True
                if quit:
                    #conn.send('\nReturning to main menu')
                    continue

                subbed_to[current_user].remove(sub_user)
                subbed_by[sub_user].remove(current_user)
                msg = '\nSuccessfully unsubscribed from: ' + sub_user
                conn.send(msg)

            # Return to main menu
            elif sel == '3':
                #conn.send('\nReturning to main menu')
                continue

        # Post a message
        elif data == '3':
            quit = False
            # Post a message
            # reply = data[len('!sendall'):]
            msg_out = '\nPlease enter a message of 140 chars or less including hashtags'
            conn.sendall(msg_out)
            tweet = conn.recv(1024)
            while len(tweet) > 140:
                msg_out = '\nMessage must be 140 chars or less. Please try again or enter \'0\' to return to main menu: \n'
                conn.sendall(msg_out)
                tweet = conn.recv(1024)
                if tweet == '0':
                    quit = True
            if quit:
                #conn.send('\nReturning to main menu')
                continue

            # Keep track of tweet + hashtags length
            len_remaining = 140 - len(tweet)
            hashtags_in = []
            # tweets[current_user][tweet] = []
            # Must have enough characters left for at least ' #' and one char
            while not quit and len_remaining > 2:
                msg_out = '\nPlease enter hashtags prepended by \'#\' and separated by newlines, or press \'0\' to proceed'
                # Subtract the space to separate the hashtags
                msg_out += '\nYou may enter ' + str(len_remaining - 1) + ' more characters including \'#\''
                conn.sendall(msg_out)
                hashtag = conn.recv(1024)
                if hashtag == '0':
                    msg_out = '\nProceeding..'
                    conn.sendall(msg_out)
                    quit = True
                elif hashtag[0] != '#':
                    msg_out = '\nPlease prepend the hashtag with \'#\' or enter \'0\' to proceed:'
                    conn.sendall(msg_out)
                    # tweets[current_user][tweet].append(hashtag)
                    # hashtag = conn.recv(1024)
                    # hashtags_in.append(hashtag)
                elif not hashtag[1:].isalnum():
                    msg_out = '\nText following \'#\' must be alphanumeric only'
                    conn.sendall(msg_out)
                elif len(hashtag) > (len_remaining):
                    msg_out = '\nToo many characters'
                    conn.sendall(msg_out)
                else:
                    # tweets[current_user][tweet].append(hashtag)
                    hashtags_in.append(hashtag)
                    # Add the 1 char space that precedes each hashtag
                    len_remaining -= (len(hashtag) + 1)


            # tweets dict key is user, value is dictionary where key is tuple of [tweet, timestamp] and value is list of hashtags
            curr_time = datetime.now()
            conn.sendall('initial time = ' + str(curr_time))
            tweets[current_user][(tweet, curr_time)] = hashtags_in

            # Push tweet to subscribers
            for user in sockets:
                if user != conn and user in subbed_by[current_user]:
                    if sockets[user] != '':
                        msg = '\n\t' + str(curr_time)
                        msg += '\n\t@' + current_user + ': '
                        msg += '\n\t' + tweet
                        for hashtags in tweets[current_user][(tweet, curr_time)]:
                            msg += ' ' + hashtags
                        msg += '\n'
                        sockets[user].sendall(msg)
                    else:
                        msg = tweet
                        for hashtags in tweets[current_user][(tweet, curr_time)]:
                            msg += ' ' + hashtags
                        if current_user not in offline[user]:
                            offline[user][current_user] = []
                        offline[user][current_user].append(msg)
            """
            for c in clients:
                if c != conn:
                    c.sendall(msg_out)
            """
            msg_out = '\nTweet posted'
            conn.sendall(msg_out)

            # TEST REMOVE
            msg = '\nYour tweets: '
            conn.sendall(msg)
            for msgs in tweets[current_user]:
                # conn.sendall('time = ' + str(curr_time))
                # conn.sendall('\ntweet = ' + tweet)
                # conn.sendall('\nmsgs[0] = ' + msgs[0] + '\nmsgs[1] = ' + str(msgs[1]))
                # conn.sendall('\ntweets[current_user][(tweet, curr_time)][0] = ' + tweets[current_user][(tweet, curr_time)][0])
                msg = '\n\t' + str(msgs[1])
                msg += '\n\t' + msgs[0]
                for hashtags in tweets[current_user][msgs]:
                #for hashtags in tweets[current_user][(tweet, curr_time)]:
                    msg += ' ' + hashtags
                conn.sendall(msg)
            conn.sendall('\n')

        elif data == '4':
            # msg = current_user + ' logging out...'
            # conn.sendall(msg)
            sockets[current_user] = ''
            offline[current_user].clear()
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
                #conn.send('\nReturning to main menu')
                continue
            #n = 1
            matches = []
            for user in tweets:
                #if n > 10:
                #    break
                for tweet in tweets[user]:
                    #if n > 10:
                #        break

                    for hashtags in tweets[user][tweet]:
                        if hashtag_in == hashtags:
                            match_tweet = [tweet[1], (user, tweet, tweets[user][tweet])]
                            matches.append(match_tweet)
                            """
                            msg = '\n' + str(n) + ') Tweet from @' + user + ': \"' + tweet[0]
                            for hashtags in tweets[user][tweet]:
                                msg += ' ' + hashtags
                            msg += '\"'
                            conn.sendall(msg)
                            """
                            #n += 1
            matches.sort(key = sortTime, reverse=True)
            if len(matches) == 0:
                conn.sendall('\nNo tweets containing ' + hashtag_in + ' found.')
            else:
                n = 1
                for match in matches:
                    """
                    conn.sendall('\nmatch[0] = ' + str(match[0]))
                    conn.sendall('\nmatch[1][0] (user) = ' + match[1][0])
                    conn.sendall('\nmatch[1][1][0] (tweet) = ' + match[1][1][0])
                    """
                    if n > 10:
                        break
                    msg = '\n' + str(n) + ') ' + str(match[0]) + ' @' + match[1][0]+ ': \"' + match[1][1][0]
                #for hashtags in tweets[current_user][msgs]:
                #for hashtags in tweets[current_user][(tweet, curr_time)]:
                    for hashtags in match[1][2]:
                        msg += ' ' + hashtags
                    msg += '\"'
                    conn.sendall(msg)
                    n += 1
            conn.sendall('\n')
                    

        else:
            reply = '\nPlease enter a valid menu item'
            conn.sendall(reply)
       
    #came out of loop
    conn.sendall('\n' + current_user + ' logging out...')
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
