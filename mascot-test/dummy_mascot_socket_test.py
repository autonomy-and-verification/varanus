import socket
import json

""" Reads the json file supplied in FILE, converts it to a list, and sends
    each event (one-by-one) to Varanus """

TCP_IP = '127.0.0.1'
TCP_PORT = 5088
BUFFER_SIZE = 1024
FILE = "scenario-traces/scenario1-trace.json"

#Open socket to Varanus
mascot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#varanus_socket.connect((TCP_IP, TCP_PORT))
mascot_socket.bind((TCP_IP, TCP_PORT))
mascot_socket.listen(1)

print("*** Dummy Mascot Listening ***")
varanus_socket, addr = mascot_socket.accept()

print("*** Dummy Mascot Reading File ***")
trace_file = open(FILE, "r")

event_list =json.load(trace_file)

trace_file.close()
print("*** Dummy Mascot Sending ***")
for event in event_list:

    # send current event to Varanus
    print("*** Dummy MASCOT Sent: " + event + " ***")
    varanus_socket.send(event)

    #Check reply
    data = varanus_socket.recv(BUFFER_SIZE)
    print("*** Dummy MASCOT Received: " + data + " ***")

mascot_socket.close()
varanus_socket.close()
