#################################################################################
# A Chat Client application. Used in the course IELEx2001 Computer networks, NTNU
#################################################################################

from socket import *
from time import sleep

# --------------------
# Constants
# --------------------
# The states that the application can be in
states = [
    "disconnected",  # Connection to a chat server is not established
    "connected",  # Connected to a chat server, but not authorized (not logged in)
    "authorized"  # Connected and authorized (logged in)
]
TCP_PORT = 1300  # TCP port used for communication
SERVER_HOST = "datakomm.work"  # Set this to either hostname (domain) or IP address of the chat server

# --------------------
# State variables
# --------------------
current_state = "disconnected"  # The current state of the system
# When this variable will be set to false, the application will stop
must_run = True
# Use this variable to create socket connection to the chat server
# Note: the "type: socket" is a hint to PyCharm about the type of values we will assign to the variable
client_socket = None  # type: socket


def quit_application():
    """ Update the application state so that the main-loop will exit. """
    # Make sure we reference the global variable here. Not the best code style,
    # but the easiest to work with without involving object-oriented code
    global must_run
    must_run = False

    return must_run


def send_command(command, arguments):
    """
    Send one command to the chat server.
    :param command: The command to send (login, sync, msg, ...(
    :param arguments: The arguments for the command as a string, or None if no arguments are needed
        (username, message text, etc). 
    :return:
    """
    global client_socket  

    what_to_send = str(command) + " " + str(arguments) + "\n"

    if arguments is None: 
        what_to_send = str(command) + "\n" 
    client_socket.send(what_to_send.encode()) 

    return what_to_send 




def read_all_inbox():
    """
    read the content of the inbox and return/ show all the message.
    First it checks the number of messages in the inbox. Then it adds
    all the messages in a list.
    :return:
    """

    global client_socket

    newline_received = False
    message = ""
    new_message = ""
    message_list = []
    x=0
    while not newline_received:  
        character = client_socket.recv(1).decode()  
        if character == '\n':  
            print(message)  
            message2 = message.strip(' inbox') 
            message2 = int(message2)           
            while x< message2: 
                character2 = client_socket.recv(1).decode() 
                if character2 == '\n': 
                    message_list.append(new_message)  
                    new_message = "" 
                    x+=1 
                elif character2 == '\r':
                    pass
                else:
                    new_message += character2 

            newline_received = True  
        elif character == '\r':  
            pass
        else:
            message += character  

    return message_list 


def get_servers_response(respond):
    """
    Wait until a response command is received from the server. 
    Reads only the first line from the server.
    :return: The response of the server, the whole line as a single string
    """

    newline_received = False
    message = ""
    while not newline_received:    
        character = respond.recv(1).decode() 
        if character == '\n':
            newline_received = True 
        elif character == '\r': 
            pass
        else:
            message += character 
    return message 



def connect_to_server():
    """
    connect to the server. Change the connection to synchronized 
    and wait for the server to respond with ok.
    :return:
    """
    # Must have these two lines, otherwise the function will not "see" the global variables that we will change here
    global client_socket
    global current_state

    client_socket = socket(AF_INET, SOCK_STREAM) 
    try:
        client_socket.connect(("datakomm.work", 1300))
        current_state = "connected" 
    except Exception as e: 
        print("Can't make a connection", str(e))

    sync = "sync" 
    try:
        send_command(sync, None) 
    except:
        print("Something went wrong")

    sleep(1) 
    connect_check = get_servers_response(client_socket) 
    if connect_check == "modeok\n" or 'modeok': 
        print(connect_check)
    else:
        print("CONNECTION NOT IMPLEMENTED!")



def disconnect_from_server():
    """
    Disconnect form server.
    :return:
    """

    global client_socket
    global current_state
    try:                        
        client_socket.close()
        current_state = "disconnected"
    except Exception as e:
        print("This happened: ", str(e)) 
    


def authorize():
    """
    This function ask the user for a username and then request the server
    using that username. If the username is already in use or invalid. A new username must
    be applied. A while loop makes sure to ask for new username until a loginok is responded
    :return:
    """
    global client_socket
    global current_state

    login = "login"
    username = input("Enter username: ")
    try:
        send_command(login, username)
    except:
        print("Something went wrong")

    sleep(1)
    check = get_servers_response(client_socket)
    while check != "loginok\n" or "loginok":
        print(check)
        print("Change username")
        username2 = input("Enter username: ")
        try:
            send_command(login, username2)
        except:
            print("Something went wrong")
        sleep(1)
        check = get_servers_response(client_socket)
        if check == "loginok\n" or "loginok":
            print(check)
            current_state = "authorized"
            break

    return None



def voxpopuli():
    """
    Send a public message. Input from the user and then tries to send it.
    Wait for the respons from the server
    :return:
    """
    global client_socket
    global current_state
    pubmessage = input("What's on your heart?: ")  
    msg = "msg"  
    try:                                    
        send_command(msg, pubmessage)
    except:
        print("Message not sent")
    sleep(1)                                       
    response = get_servers_response(client_socket)  
    print(response)


def inbox():
    """
    This function is used to check the inbox and see the content inside.
    :return:
    """
    global client_socket
    global current_state
    mail= "inbox" 
    try:                        
        send_command(mail, None)
    except:                     
        print("Could not see inbox")
    sleep(1)                       
    response = read_all_inbox()   
    print(response)


def privmessage():
    """
    Send a private message to someone. The program ask what to send and to whom. 
    Then tries to send it and wait for a respons form the server if it was successful
    :return:
    """
    global client_socket
    global current_state

    privmsg = "privmsg"                                             
    to_whom = input("To whom would you like to send a message: ")   
    messag = input("What would you like to send: ")
    both = str(to_whom) + " " + str(messag)                         
    try:                                                            
        send_command(privmsg, both)
    except:
        print("Something went wrong")
    sleep(1)                                        
    response = get_servers_response(client_socket)  
    print(response)


def list_of_all_users():
    """
    Function to see all the users connected to the server at that particular moment
    :return:
    """
    global client_socket
    global current_state

    users = "users"                
    try:                           
        send_command(users, None)
    except:
        print("Something went wrong")
    sleep(1)                                        
    response = get_servers_response(client_socket)  
    print(response)

    return response



"""
The list of available actions that the user can perform
Each action is a dictionary with the following fields:
description: a textual description of the action
valid_states: a list specifying in which states this action is available
function: a function to call when the user chooses this particular action. The functions must be defined before
            the definition of this variable
"""
available_actions = [
    {
        "description": "Connect to a chat server",
        "valid_states": ["disconnected"],
        "function": connect_to_server
    },
    {
        "description": "Disconnect from the server",
        "valid_states": ["connected", "authorized"],
        "function": disconnect_from_server
    },
    {
        "description": "Authorize (log in)",
        "valid_states": ["connected", "authorized"],
        "function": authorize
    },
    {
        "description": "Send a public message",
        "valid_states": ["connected", "authorized"],
        "function": voxpopuli
    },
    {
        "description": "Send a private message",
        "valid_states": ["authorized"],
        "function": privmessage
    },
    {
        "description": "Read messages in the inbox",
        "valid_states": ["connected", "authorized"],
        "function": inbox
    },
    {
        "description": "See list of users",
        "valid_states": ["connected", "authorized"],
        "function": list_of_all_users
    },
    {
        "description": "Get a joke",
        "valid_states": ["connected", "authorized"],
        "function": None
    },
    {
        "description": "Quit the application",
        "valid_states": ["disconnected", "connected", "authorized"],
        "function": quit_application
    },
]


def run_chat_client():
    """ Run the chat client application loop. When this function exists, the application will stop """

    while must_run:
        print_menu()
        action = select_user_action()
        perform_user_action(action)
    print("Thanks for watching. Like and subscribe! 👍")


def print_menu():
    """ Print the menu showing the available options """
    print("==============================================")
    print("What do you want to do now? ")
    print("==============================================")
    print("Available options:")
    i = 1
    for a in available_actions:
        if current_state in a["valid_states"]:
            # Only hint about the action if the current state allows it
            print("  %i) %s" % (i, a["description"]))
        i += 1
    print()


def select_user_action():
    """
    Ask the user to choose and action by entering the index of the action
    :return: The action as an index in available_actions array or None if the input was invalid
    """
    number_of_actions = len(available_actions)
    hint = "Enter the number of your choice (1..%i):" % number_of_actions
    choice = input(hint)
    # Try to convert the input to an integer
    try:
        choice_int = int(choice)
    except ValueError:
        choice_int = -1

    if 1 <= choice_int <= number_of_actions:
        action = choice_int - 1
    else:
        action = None

    return action


def perform_user_action(action_index):
    """
    Perform the desired user action
    :param action_index: The index in available_actions array - the action to take
    :return: Desired state change as a string, None if no state change is needed
    """
    if action_index is not None:
        print()
        action = available_actions[action_index]
        if current_state in action["valid_states"]:
            function_to_run = available_actions[action_index]["function"]
            if function_to_run is not None:
                function_to_run()
            else:
                print("Internal error: NOT IMPLEMENTED (no function assigned for the action)!")
        else:
            print("This function is not allowed in the current system state (%s)" % current_state)
    else:
        print("Invalid input, please choose a valid action")
    print()
    return None

# Entrypoint for the application. In PyCharm you should see a green arrow on the left side.
# By clicking it you run the application.
if __name__ == '__main__':
    run_chat_client()
