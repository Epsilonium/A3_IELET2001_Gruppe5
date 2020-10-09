#################################################################################
# A Chat Client application. Used in the course IELEx2001 Computer networks, NTNU
#################################################################################

from socket import *
from time import sleep
"""
What are missing 05.10.20
Joke function
"""

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
        (username, message text, etc). Finiseh!!!
    :return:
    """
    global client_socket  #Trenger denne til å sende

    what_to_send = str(command) + " " + str(arguments) + "\n" #Slår sammen kommandoen og argumentet i en string. + newline

    if arguments is None: #Tilfelle det ikke er noen argument
        what_to_send = str(command) + "\n" #Må likevel legge til newline
    client_socket.send(what_to_send.encode()) #encode og send

    return what_to_send #Trenger egt ikke å returnere noe




def read_all_inbox():
    """
    read the content of the inbox and return/ show all the messages
    :return:
    """

    global client_socket

    newline_received = False #Ulike variabler vi behøver
    message = ""
    new_message = ""
    message_list = []
    x=0
    while not newline_received:  # while løkke så lenge variabelen ikke er True
        character = client_socket.recv(1).decode()  # Leser av data med bufsize 1 og dekoder
        if character == '\n':  # Sjekker om data inn er newline
            print(message)   #printer hva vi har fått
            message2 = message.strip(' inbox') #fjerner inbox fra stringen slik at vi sitter igjen
            message2 = int(message2)           #med antallet meldinger
            while x< message2: #While løkke som skal iterere over antallet meldinger vi har fått
                character2 = client_socket.recv(1).decode() #Leser av data med bufsize 1 og dekoder
                if character2 == '\n': #Sjekker om dataen er newline
                    message_list.append(new_message)  #Legger til medlingen i lista
                    new_message = "" #Tømmer stringen slik at adderer hver melding etter hverandre
                    x+=1 #Øker x når vi har lagt en av meldingene
                elif character2 == '\r':
                    pass
                else:
                    new_message += character2 #legger hver innkommende data i en string

            newline_received = True  # Variabelen blir True og vi kan hoppe ut av while løkka
        elif character == '\r':  # Eller hvis data inn er \r hobber vi videre
            pass
        else:
            message += character  # Legger til dataen i stringen for meldingen

    return message_list #returner lista med meldinger


def get_servers_response(respond):
    """
    Wait until a response command is received from the server. Finished i think
    :return: The response of the server, the whole line as a single string
    """

    newline_received = False
    message = ""
    while not newline_received:    #while løkke så lenge variabelen ikke er True
        character = respond.recv(1).decode() # Leser av data med bufsize 1 og dekoder
        if character == '\n': #Sjekker om data inn er newline
            newline_received = True #Variabelen blir True og vi kan hoppe ut av while løkka
        elif character == '\r': # Eller hvis data inn er \r hobber vi videre
            pass
        else:
            message += character #Legger til dataen i stringen for meldingen
    return message #Returnerer medlingen



def connect_to_server():
    """
    connect til serveren. endre til sync mode og
    :return:
    """
    # Must have these two lines, otherwise the function will not "see" the global variables that we will change here
    global client_socket
    global current_state

    client_socket = socket(AF_INET, SOCK_STREAM) #Standard prosedyre
    try:
        client_socket.connect(("datakomm.work", 1300)) #Prøver å koble oss til på addresse og port
        current_state = "connected" #Hvis det går endret vi current state til å være pålogget
    except Exception as e: #Hvis jeg får feilmelding. printer en melding på at feil
        print("Can't make a connection", str(e))

    sync = "sync" #Kommando
    try:
        send_command(sync, None) #Prøver å sende kommandoen, og sjekker om det oppstår feil
    except:
        print("Something went wrong")

    sleep(1) #avventer litt for at programmet ikke skal rspondere raskere enn serveren 
    connect_check = get_servers_response(client_socket) #Lagrer responsen fra serveren
    if connect_check == "modeok\n" or 'modeok': #Sjekker om responsen er grei
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
    try:                        #Prøver å disconnecte fra serveren
        client_socket.close()
        current_state = "disconnected"
    except Exception as e:
        print("This happened: ", str(e)) # hvis det oppstår feil printer en feilmelding
    current_state = "disconnected" #Endrer current_state til disconnect


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
    Send a public message.
    :return:
    """
    global client_socket
    global current_state
    pubmessage = input("What's on your heart?: ")  #Meldingen
    msg = "msg"  #kommandoen
    try:                                    #Prøver å sende kommandoen og feilmelding hvis noe går galt
        send_command(msg, pubmessage)
    except:
        print("Message not sent")
    sleep(1)                                        #Avventer
    response = get_servers_response(client_socket)  #Lagrer responsen og printer
    print(response)


def inbox():
    """
    This function is used to check the inbox and see the content inside.
    :return:
    """
    global client_socket
    global current_state
    mail= "inbox" #protkollen
    try:                        #Prøver å sende kommandoen for å se innboksen
        send_command(mail, None)
    except:                     #hvis feil oppstår print en feilmelding
        print("Could not see inbox")
    sleep(1)                       #avventer for at serveren skal få sende en respons
    response = read_all_inbox()    #Lager innholdet i inboxen i e variabel
    print(response)


def privmessage():
    """
    Send a private message to someone.
    :return:
    """
    global client_socket
    global current_state

    privmsg = "privmsg"                                             #Kommandoen
    to_whom = input("To whom would you like to send a message: ")   #Hvem og hva man ønsker å sende
    messag = input("What would you like to send: ")
    both = str(to_whom) + " " + str(messag)                         #Samler de til en variebel
    try:                                                            #Prøver å sende, og printer en feilmelding hvis noe går galt
        send_command(privmsg, both)
    except:
        print("Something went wrong")
    sleep(1)                                        #Avventer
    response = get_servers_response(client_socket)  #Lagrer responsen og printer
    print(response)


def list_of_all_users():
    """
    Function to see all the users
    :return:
    """
    global client_socket
    global current_state

    users = "users"                 #kommendoen
    try:                            #Prøver å sende kommandoen og printer hvis noe går galt
        send_command(users, None)
    except:
        print("Something went wrong")
    sleep(1)                                        #Avventer
    response = get_servers_response(client_socket)  #Lagrer responsen og printer den
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
        # TODO - optional step - implement the joke fetching from the server.
        # Hint: this part is not described in the protocol. But the command is simple. Try to find
        # out how it works ;)
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